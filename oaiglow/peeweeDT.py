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
		self.draw = None,
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
	'''

	def __init__(self, columns, peewee_model, DTinput):

		logging.debug(DTinput)
		
		# columns to parse from table rows
		self.columns = columns

		# peewee model
		self.peewee_model = peewee_model

		# dictionary INPUT DataTables ajax
		self.DTinput = DTinput
		logging.debug(self.DTinput)

		# placeholder for query to build
		self.query = False
		self.query_slice = False

		# dictionary OUTPUT to DataTables
		self.DToutput = DT().__dict__
		self.DToutput['draw'] = DTinput['draw']

		# query and build response
		self.build_response()


	def filter(self):
		logging.debug('applying filters...')

		'''
		searching title, abstract, and identifier columns
		'''

		search_string = self.DTinput['search']['value']
		if search_string != '':
			self.query = self.query.where(
				(self.peewee_model.title.contains(search_string)) |
				(self.peewee_model.abstract.contains(search_string)) |
				(self.peewee_model.identifier.contains(search_string))
			)


	def sort(self):
		
		'''
		Iterate through order_by columns
		'''
		
		logging.debug('sorting...')

		# get sort column
		for order in self.DTinput['order']:
			order_by_column = getattr(self.peewee_model,self.columns[order['column']])
			order_by_dir = order['dir']
			logging.debug('ordering by %s, %s' % (order_by_column, order_by_dir))
			if order_by_dir == 'asc':
				self.query = self.query.order_by(order_by_column.asc())
			if order_by_dir == 'desc':
				self.query = self.query.order_by(order_by_column.desc())
			


	def paginate(self):

		logging.debug('paginating...')

		# using offset (start) and limit (length)
		self.query_slice = self.query.offset(self.DTinput['start']).limit(self.DTinput['length'])


	def build_response(self):

		logging.debug('building query...')

		# begin query
		self.query = self.peewee_model.select()

		# update DToutput
		self.DToutput['recordsTotal'] = self.query.count()

		# apply filtering
		self.filter()
		self.sort()
		self.paginate()

		# build DToutput
		self.DToutput['recordsFiltered'] = self.query.count()

		logging.debug(self.DToutput)

		# iterate through rows
		logging.debug('iterate through rows...')
		for row in self.query_slice:

			'''
			This would be an option for filters, like the ones provided through dataTables-SQL library leveraged here:
			https://github.com/WSULib/ouroboros/blob/v2/WSUDOR_Manager/actions/ingestWorkspace/__init__.py#L255-L281
			'''

			# iterate through columns and place in list
			row_data = [ getattr(row, column)  for column in self.columns  ]

			# add list to object
			self.DToutput['data'].append(row_data)


	def to_json(self):

		return json.dumps(self.DToutput)


