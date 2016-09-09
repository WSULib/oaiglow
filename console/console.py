# oaiglow console

# generic
import logging
from lxml import etree
logging.basicConfig(level=logging.DEBUG)
import re

# oaiglow
import localConfig
from oaiglow.models import Server, Identifier, Record
from oaiglow import db
db.connect()
import sickle


logging.debug('''
    _------_
  -~        ~-
 -     _      -
-      |>      -
-      |<      -
 -     |>     -
  -    ||    -
   -   ||   -
    -__||__-
    |______|
    <______>
    <______>
       \/''')

print('''
Welcome to oaiglow console.

testLiveServer() - init connection to configured OAI server, get test_records
tableWipe() - wipe and recreate tables
testIdentifier() = return test identifier
staticRecords() = returns parsed static records
staticSickleRecords([list_of_records]) = returns list of Sickle records from raw OAI server XML records, i.e. results of staticRecords() (shorthand: `sickle_records = staticSickleRecords(staticRecords())` )
staticOGRecords() = returns initiated 
''')

server = False
identifiers = False
test_records = False
cfai_example = False
def testLiveServer():
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
	logging.debug('dropping tables...')
	for table in [Identifier,Record]:
		try:
			db.drop_table(table)
		except:
			logging.debug('could not drop table, %s' % table)
	logging.debug('creating tables...')
	db.create_tables([Identifier,Record])

# test store and retrieve identifier
def testIdentifier():
	sickle_test_ident = identifiers.next()
	logging.debug('storing identifier...')
	ident_row = Identifier.create(sickle_test_ident)
	ident_row.save()
	logging.debug('retrieving identifier...')
	logging.debug( Identifier.select().where(Identifier.identifier == sickle_test_ident.identifier).get() )


# get test records from static file
def staticRecords():
	with open('oaiglow/static/xml/mods_sample_records.xml') as fhand:
		records = re.findall(r'(<record.+?</record>)', fhand.read())
		return [ etree.fromstring(record) for record in records ]

def staticSickleRecords(records=staticRecords()):
	return [ sickle.models.Record(record) for record in records ]

def staticOGRecords(sickle_records=staticSickleRecords()):
	return [ Record.create(sickle_record) for sickle_record in sickle_records ]