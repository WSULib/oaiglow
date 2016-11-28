# oaiglow models

# localConfig
import localConfig

# peewee ORM
import peewee

# Sickle
from sickle import Sickle

# oaiglow
from oaiglow import db, logging

# generic
from lxml import etree, isoschematron


# OAI-PMH server
class Server(object):

	'''
	app wrapper for sickle OAI-PMH serer interface
	'''
	
	def __init__(self, base_url=localConfig.OAI_SERVER_BASE_URL, default_set=localConfig.OAI_SET, default_metadata_prefix=localConfig.OAI_METADATA_PREFIX):
		self.base_url = base_url
		self.default_set = default_set
		self.default_metadata_prefix = default_metadata_prefix

		# init sickle interface
		self.sickle = Sickle(self.base_url)


	def get_record(self, identifier, metadataPrefix=localConfig.OAI_METADATA_PREFIX):
		'''
		todo: add try / except block here
		'''
		sickle_record = self.sickle.GetRecord(identifier=identifier, metadataPrefix=metadataPrefix)
		return Record.create(sickle_record)


class Identifier(peewee.Model):

	'''
	ORM wrapper for Sickle Identifier
	'''

	datestamp = peewee.DateField()
	deleted = peewee.BooleanField()
	identifier = peewee.CharField()
	raw = peewee.CharField()
	setSpecs = peewee.CharField()
	xml = None

	class Meta:
		database = db

	@classmethod
	def create(cls, sickle_identifier_record):
		return cls(
			datestamp=sickle_identifier_record.datestamp,
			deleted=sickle_identifier_record.deleted,
			identifier=sickle_identifier_record.identifier,
			raw=sickle_identifier_record.raw,
			setSpecs=sickle_identifier_record.setSpecs,xml=sickle_identifier_record.xml
		)


class Record(peewee.Model):
	
	'''
	ORM wrapper for Sickle Record
	'''

	# DB fields
	# full record
	raw = peewee.TextField()

	# header
	identifier = peewee.CharField()
	datestamp = peewee.DateField()
	setSpec = peewee.CharField()

	# metadata (payload and derived)
	metadata_as_string = peewee.TextField()
	title = peewee.TextField()
	abstract = peewee.TextField()
	primary_url = peewee.CharField()
	thumbnail_url = peewee.CharField()

	# validations
	schematron_validation_score = peewee.FloatField()

	# about
	'''
	Skipping about section from REPOX for now, looks to be showing provenance of original record?
	'''

	# not stored in DB
	# xml etree element
	metadata = None

	# sickle API
	sickle = None

	# OAI-PMH server
	server = Server()

	class Meta:
		database = db
		only_save_dirty = True


	@classmethod
	def get(cls, identifier):
		logging.debug('getting db record')
		query = cls.select().where(Record.identifier==identifier).execute()		
		try:
			return query.next()
		except StopIteration:
			return False


	@classmethod
	def create(cls, sickle_record):
		
		#raw
		raw = sickle_record.raw

		# header
		header = sickle_record.xml.find('{http://www.openarchives.org/OAI/2.0/}header')
		identifier = header.find('{http://www.openarchives.org/OAI/2.0/}identifier').text
		datestamp = header.find('{http://www.openarchives.org/OAI/2.0/}datestamp').text
		setSpec = header.find('{http://www.openarchives.org/OAI/2.0/}setSpec').text

		#metadata
		metadata = sickle_record.xml.find('{http://www.openarchives.org/OAI/2.0/}metadata').getchildren()[0]
		metadata_as_string = etree.tostring(metadata)
		title = sickle_record.metadata['title'][0]
		abstract = sickle_record.metadata['abstract'][0]

		# validations
		schematron_validation_score = 0.0
		
		# extract URLs
		#####################################################################################################################
		# xpath
		# primary_url = metadata.xpath('//mods:url[@usage="primary"]', namespaces={'mods':'http://www.loc.gov/mods/v3'})[0].text
		# thumbnail_url = metadata.xpath('//mods:url[@access="preview"]', namespaces={'mods':'http://www.loc.gov/mods/v3'})[0].text
		
		# findall
		primary_url = metadata.find('{http://www.loc.gov/mods/v3}location/{http://www.loc.gov/mods/v3}url[@usage="primary"]').text
		thumbnail_url = metadata.find('{http://www.loc.gov/mods/v3}location/{http://www.loc.gov/mods/v3}url[@access="preview"]').text
		#####################################################################################################################

		# return Record Instance
		return cls(
			raw=raw,
			identifier=identifier,
			datestamp=datestamp,
			setSpec=setSpec,
			metadata_as_string=metadata_as_string,
			title=title,
			abstract=abstract,
			primary_url=primary_url,
			thumbnail_url=thumbnail_url,
			metadata=metadata,
			sickle=sickle_record,
			schematron_validation_score=schematron_validation_score
		)


	# update record from OAI-PMH server
	def update_from_server(self):

		logging.info("updating record: %s" % self.identifier)

		# delete db instance
		logging.debug("deleteing db instance")
		self.delete_instance()

		# create from new
		logging.debug("retrieving record from OAI-PMH server")
		self = self.server.get_record(self.identifier)

		# save to db 
		logging.debug('saving new instance to db')
		self.save()


	def validate_schematrons(self):

		'''
		Validate schematrons
		'''

		logging.debug("validating schematrons for %s" % self.identifier)

		# result dictionary
		validation_results = []

		# get current schematron validations
		schematrons = Schematron.select()

		for schematron in schematrons:
			logging.info("validating on %s / %s" % (schematron.name, schematron.filename))
			sct_doc = etree.fromstring(schematron.xml.encode('utf-8'))
			validator = isoschematron.Schematron(sct_doc, store_report=True)
			# prepare metadata
			self.metadata = etree.fromstring(self.metadata_as_string)
			# validate
			is_valid = validator.validate(self.metadata)

			# add to results dictionary
			validation_results.append({
				'schematron':schematron,
				'result':is_valid,
				'validator':validator
			})

		self.validation_results = validation_results

		# update schematron_validation_score
		val_bools = [ test['result'] for test in self.validation_results ]
		self.schematron_validation_score = sum(val_bools) / len(val_bools)
		logging.debug("updating schematron_validation_score to %s" % self.schematron_validation_score)
		self.save()

		return validation_results
			

class Schematron(peewee.Model):

	'''
	ORM wrapper for Schematron validation files
	'''

	name = peewee.CharField()
	filename = peewee.CharField()
	xml = peewee.TextField()

	class Meta:
		database = db


	@classmethod
	def create(cls, name, filename, xml):
		return cls(
			name=name,
			filename=filename,
			xml=xml,
		)














