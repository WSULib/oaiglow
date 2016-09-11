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
from lxml import etree


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
	raw= peewee.CharField()
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
	thumbnail_url = peewee.CharField()

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
		thumbnail_url = metadata.xpath('//mods:url[@access="preview"]', namespaces={'mods':'http://www.loc.gov/mods/v3'})[0].text

		# return Record Instance
		return cls(
			raw=raw,
			identifier=identifier,
			datestamp=datestamp,
			setSpec=setSpec,
			metadata_as_string=metadata_as_string,
			title=title,
			thumbnail_url=thumbnail_url,
			metadata=metadata,
			sickle=sickle_record
		)


	# update record from OAI-PMH server
	def update(self):

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






















