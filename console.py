# oaiglow console

import logging
logging.basicConfig(level=logging.DEBUG)

import localConfig
from oaiglow.models import Server, Identifier, Record
from oaiglow import db
db.connect()

# fire sickle server instance
logging.debug('firing server instance...')
server = Server()

# load identifiers
identifiers = server.sickle.ListIdentifiers(metadataPrefix=localConfig.OAI_METADATA_PREFIX)

# test records
logging.debug('loading test identifiers...')
test_records = [ server.get_record(ident) for ident in localConfig.TEST_IDENTIFIERS ]
cfai_example = test_records[0]

# DB
def tableWipe():
	db.drop_table(Identifier)
	db.create_tables([Identifier])

# test store and retrieve identifier
def testIdentifier():
	test_ident = identifiers.next()
	logging.debug('storing identifier...')
	ident_row = Identifier(datestamp=test_ident.datestamp, deleted=test_ident.deleted, identifier=test_ident.identifier, raw=test_ident.raw, setSpecs=test_ident.setSpecs, xml=test_ident.xml)
	ident_row.save()
	logging.debug('retrieving identifier...')
	logging.debug( Identifier.select().where(Identifier.identifier == test_ident.identifier).get() )

