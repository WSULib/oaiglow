# oaiglow console

# generic
from lxml import etree
import re
import time


# oaiglow
import localConfig
from localConfig import logging

from oaiglow.models import Server, Identifier, Record, Schematron
from oaiglow import db
db.connect()
import sickle


print('''
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
Welcome to oaiglow console.''')


# init server
server = Server()


# DB
def db_init():
	'''
	move to method somewhere
	'''
	logging.debug('dropping tables...')
	for table in [Identifier,Record,Schematron]:
		try:
			db.drop_table(table)
		except:
			logging.debug('could not drop table, %s' % table)
	logging.debug('creating tables...')
	db.create_tables([Identifier,Record,Schematron])


