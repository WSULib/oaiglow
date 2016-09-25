# peewee / dataTables connector

##################################################################
# Inspired by: https://github.com/Pegase745/sqlalchemy-datatables
##################################################################

import json

from logging import getLogger
logging = getLogger('peeweeDT')

class PeeweeDT(object):

	def __init__(self, columns, peewee_model, DTjson):

		logging.debug(DTjson)
		
		self.columns = columns
		self.peewee_model = peewee_model
		self.DTjson = DTjson


	def to_json(self):

		return json.dumps({'msg':'fake gators'})