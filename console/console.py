# oaiglow console

# generic
from lxml import etree
import re
import time


# oaiglow
import localConfig
from localConfig import logging

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
staticOGRecords() = returns oaiglow records
insertAll(insert_type=['atomic','insert_many'] = inserts all static OG records, iterating or insert_many, both with `db.atomic()`
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


def insertAll(og_records=staticOGRecords()):

	# atomic
	'''
	If debug printing is off, this is plenty fast enough:
		~ 2300 records = 1.1 seconds
	'''
	stime = time.time()
	with db.atomic():
		for og in og_records:
			og.save()
	logging.info("total time for insert: %s" % (float(time.time()) - float(stime)))