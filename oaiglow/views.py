# views for oaiglow

# flask proper
from flask import render_template, request, session, redirect, make_response, Response

# oaiglow flask app
from oaiglow import db, logging, oaiglow_app, server
from oaiglow.models import Server, Identifier, Record

# localConfig
import localConfig

# generic
import time

####################
# HOME
####################

# home index
@oaiglow_app.route("/%s/" % (localConfig.OAIGLOW_APP_PREFIX), methods=['POST', 'GET'])
@oaiglow_app.route("/%s" % (localConfig.OAIGLOW_APP_PREFIX), methods=['POST', 'GET'])
def index():	

	return render_template("index.html", localConfig=localConfig)


####################
# HARVEST
####################

# harvest home
@oaiglow_app.route("/%s/harvest/" % (localConfig.OAIGLOW_APP_PREFIX), methods=['POST', 'GET'])
@oaiglow_app.route("/%s/harvest" % (localConfig.OAIGLOW_APP_PREFIX), methods=['POST', 'GET'])
def harvest():

	return render_template("harvest.html", localConfig=localConfig)


# harvest all records
@oaiglow_app.route("/%s/harvest/all/" % (localConfig.OAIGLOW_APP_PREFIX), methods=['POST', 'GET'])
@oaiglow_app.route("/%s/harvest/all" % (localConfig.OAIGLOW_APP_PREFIX), methods=['POST', 'GET'])
def harvest_all():

	'''
	Use bulk inserts:
	file:///home/commander/websites/peewee_docs/docs.peewee-orm.com/en/latest/peewee/querying.html#bulk-inserts
	'''

	logging.debug("preparing to harvest all records")

	# retrieve records to harvest and store in DB
	records = server.sickle.ListRecords(metadataPrefix=localConfig.OAI_METADATA_PREFIX)
	total_count = records.resumption_token.complete_list_size

	with db.atomic():
		stime = time.time()
		for record in records:
			og_record = Record.create(record)
			og_record.save()
		logging.info("total records, total time: %s, %s seconds" % (total_count, (float(time.time()) - stime)))

	return render_template("harvest.html", localConfig=localConfig, app_msg="%s records harvested, total time elapsed %s seconds" % (total_count, (float(time.time()) - stime)))


# wipe all records
@oaiglow_app.route("/%s/harvest/wipe/" % (localConfig.OAIGLOW_APP_PREFIX), methods=['POST', 'GET'])
@oaiglow_app.route("/%s/harvest/wipe" % (localConfig.OAIGLOW_APP_PREFIX), methods=['POST', 'GET'])
def wipe():

	# dropping and creating tables
	logging.info('dropping tables...')
	for table in [Identifier,Record]:
		try:
			db.drop_table(table)
		except:
			logging.info('could not drop table, %s' % table)
	logging.info('creating tables...')
	db.create_tables([Identifier,Record])
	logging.info("tableWipe complete.")

	return render_template("harvest.html", localConfig=localConfig, app_msg="tables wiped and created")



####################
# VIEW
####################

# view home
@oaiglow_app.route("/%s/view/" % (localConfig.OAIGLOW_APP_PREFIX), methods=['POST', 'GET'])
@oaiglow_app.route("/%s/view" % (localConfig.OAIGLOW_APP_PREFIX), methods=['POST', 'GET'])
def view():

	return render_template("view.html", localConfig=localConfig)


# view all records
@oaiglow_app.route("/%s/view/all/" % (localConfig.OAIGLOW_APP_PREFIX), methods=['POST', 'GET'])
@oaiglow_app.route("/%s/view/all" % (localConfig.OAIGLOW_APP_PREFIX), methods=['POST', 'GET'])
def view_all():

	# get all records
	all_records = list(Record.select())

	return render_template("view_all.html", localConfig=localConfig, all_records=all_records)


####################
# RECORD
####################

# view all records
@oaiglow_app.route("/%s/record/<identifier>/" % (localConfig.OAIGLOW_APP_PREFIX), methods=['POST', 'GET'])
@oaiglow_app.route("/%s/record/<identifier>" % (localConfig.OAIGLOW_APP_PREFIX), methods=['POST', 'GET'])
def single_record(identifier):

	# retrieve single record from OAI server
	record = server.get_record(identifier)

	return render_template("record_single.html",localConfig=localConfig, record=record)


####################
# REPORTS
####################

