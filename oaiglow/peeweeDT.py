# peewee / dataTables connector

##################################################################
# Inspired by: https://github.com/Pegase745/sqlalchemy-datatables
##################################################################

import json

from logging import getLogger
logging = getLogger('peeweeDT')


class DT(object):

	'''
	Scaffolding for DT response
	'''

	def __init__(self):
		self.draw = 1,
		self.recordsTotal = None,
		self.recordsFiltered = None,
		self.data = []


class PeeweeDT(object):

	'''
	Order of operations:
		- init 
		- query
		- filter / slice / order / etc.
		- build response
		- return json

	DTinput will look like this...
	{
	  "args": {
		"draw": 1,
		"columns": [
		  {
			"data": "data0",
			"searchable": true,
			"orderable": true,
			"search": {
			  "value": "",
			  "regex": false
			}
		  },
		  {
			"data": "data1",
			"searchable": true,
			"orderable": true,
			"search": {
			  "value": "",
			  "regex": false
			}
		  },
		],
		"order": [],
		"start": 0,
		"length": 100,
		"search": {
		  "value": "",
		  "regex": false
		}
	  }
	}
	'''

	def __init__(self, columns, peewee_model, DTinput):

		logging.debug(DTinput)
		
		# columns to parse from table rows
		self.columns = columns

		# peewee model
		self.peewee_model = peewee_model

		# dictionary INPUT DataTables ajax
		self.DTinput = DTinput

		# placeholder for query to build
		self.query = False

		# dictionary OUTPUT to DataTables
		self.DToutput = DT()

		# query and build response
		self.build_response()


	def query_init(self):

		self.query = self.peewee_model.select()
		self.DToutput.recordsTotal = self.query.count()


	def filter(self):
		logging.debug('applying filters...')


	def paginate(self):
		logging.debug('paginating...')
		# self.query = self.query.paginate(self.DTinput['start'], self.DTinput['length'])
		logging.debug('donw!~')


	def build_response(self):

		logging.debug('building query...')

		# begin query
		self.query_init()

		# apply filtering
		self.filter()
		self.paginate()

		logging.debug('made it...')

		# build DToutput
		self.DToutput.recordsFiltered = self.query.count()

		# iterate through rows
		logging.debug('iterate through rows and building response dictionary...')
		for row in self.query:
			logging.debug(row)

			# iterate through columns and place in list
			row_data = [ getattr(row, column)  for column in self.columns  ]

			# add list to object
			self.DToutput.data.append(row_data)

		logging.debug(self.to_json())

		# return as json
		return self.to_json()


	def to_json(self):

		return json.dumps(self.DToutput.__dict__)


