# views for oaiglow

# flask proper
from flask import render_template, request, session, redirect, make_response, Response

# oaiglow flask app
from oaiglow import oaiglow_app, db, logging
from oaiglow.models import Server, Identifier, Record

# localConfig
import localConfig


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

	# DEBUG - using static records
	from console import console
	# grab statics
	ogs = console.staticOGRecords()
	# ingest statics
	with db.atomic():
		for og in ogs:
			og.save()

	return render_template("harvest_status.html", localConfig=localConfig, harvest_count=len(ogs))


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