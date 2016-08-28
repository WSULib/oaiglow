# oaiglow models

# localConfig
import localConfig

# peewee ORM
from peewee import *

# Sickle
from sickle import Sickle

class Server(object):

	'''
	wrapper for sickle OAI-PMH serer interface
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
		return Record(identifier, sickle_record)


class Record(object):
	
	'''
	wrapper for Sickle Record
	'''

	def __init__(self, identifier, sickle_record):
		self.identifier = identifier
		self.sickle = sickle_record

		# read XML, derive common values
		self.metadata = self.sickle.xml.find('{http://www.openarchives.org/OAI/2.0/}metadata')
		self.title = self.sickle.metadata['title'][0]
		self.thumbnail_url = self.metadata.xpath('//mods:url[@access="preview"]', namespaces={'mods':'http://www.loc.gov/mods/v3'})[0].text

	def __repr__(self):
		return "<dplamp.oai.Record: %s / %s>" % (self.title, self.identifier)

	def __str__(self):
		return "<dplamp.oai.Record: %s / %s>" % (self.title, self.identifier)