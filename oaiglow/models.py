# oaiglow models

# localConfig
import localConfig

# peewee ORM
import peewee

# Sickle
from sickle import Sickle

# oaiglow
from oaiglow import db


class Server(object):

	'''
	app wrapper for sickle OAI-PMH serer interface
	'''
	
	def __init__(self):
		self.base_url = localConfig.OAI_SERVER_BASE_URL
		self.default_set = localConfig.OAI_SET
		self.default_metadata_prefix = localConfig.OAI_METADATA_PREFIX

		# init sickle interface
		self.sickle = Sickle(self.base_url)


	def get_record(self, identifier, metadataPrefix=localConfig.OAI_METADATA_PREFIX):
		'''
		todo: add try / except block here
		'''
		sickle_record = self.sickle.GetRecord(identifier=identifier, metadataPrefix=metadataPrefix)
		return Record.create(identifier, sickle_record)


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
	identifier = peewee.CharField()
	title = peewee.CharField()
	thumbnail_url = peewee.CharField()

	# not stored in DB
	# xml etree element
	metadata = None

	# sickle API
	sickle = None

	class Meta:
		database = db

	@classmethod
	def create(cls, identifier, sickle_record):
		metadata = sickle_record.xml.find('{http://www.openarchives.org/OAI/2.0/}metadata')
		title = sickle_record.metadata['title'][0]
		thumbnail_url = metadata.xpath('//mods:url[@access="preview"]', namespaces={'mods':'http://www.loc.gov/mods/v3'})[0].text
		return cls(
			identifier=identifier,
			title=title,
			thumbnail_url=thumbnail_url,
			metadata=metadata,
			sickle=sickle_record
		)














