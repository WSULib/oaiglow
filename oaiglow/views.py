# views for oaiglow

# flask proper
from flask import render_template, request, session, redirect, make_response, Response, jsonify

# oaiglow flask app
from oaiglow import db, logging, oaiglow_app, server
from oaiglow.models import Identifier, Record

# peeweeDT
from oaiglow.peeweeDT import PeeweeDT

# localConfig
import localConfig

# generic
from lxml import etree
import json
import time
import urllib

####################
# HOME
####################

# home index
@oaiglow_app.route("/", methods=['POST', 'GET'])
def index():	

	return render_template("index.html", localConfig=localConfig)


####################
# HARVEST
####################

# harvest home
@oaiglow_app.route("/harvest", methods=['POST', 'GET'])
def harvest():

	return render_template("harvest.html", localConfig=localConfig)


# harvest all records
@oaiglow_app.route("/harvest/all", methods=['POST', 'GET'])
def harvest_all():

	'''
	Use bulk inserts:
	file:///home/commander/websites/peewee_docs/docs.peewee-orm.com/en/latest/peewee/querying.html#bulk-inserts
	'''

	logging.debug("preparing to harvest all records")

	# retrieve records to harvest and store in DB
	records = server.sickle.ListRecords(metadataPrefix=localConfig.OAI_METADATA_PREFIX)
	total_count = records.resumption_token.complete_list_size

	'''
	Need to rework.  xpath retrieval of URLs are getting bungled.
	'''

	# with db.atomic():
	stime = time.time()
	for record in records:
		og_record = Record.create(record)
		og_record.save()
	logging.info("total records, total time: %s, %s seconds" % (total_count, (float(time.time()) - stime)))

	return render_template("harvest.html", localConfig=localConfig, app_msg="%s records harvested, total time elapsed %s seconds" % (total_count, (float(time.time()) - stime)))


# wipe all records
@oaiglow_app.route("/harvest/wipe", methods=['POST', 'GET'])
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
@oaiglow_app.route("/view", methods=['POST', 'GET'])
def view():

	# get all records
	all_records = list(Record.select())

	return render_template("view.html", localConfig=localConfig, all_records=all_records)



####################
# ABOUT
####################

# view home
@oaiglow_app.route("/about", methods=['POST', 'GET'])
def about():

	return render_template("about.html", localConfig=localConfig)


####################
# REPORTS
####################

# view home
@oaiglow_app.route("/reports", methods=['POST', 'GET'])
def reports():

	return render_template("reports.html", localConfig=localConfig)



#####################
# Datatables Endpoint
#####################

# return json for job
@oaiglow_app.route('/view/all/datatables_json', methods=['POST', 'GET'])
def datatables_json():

	'''
	Expecting JSON request from DataTables here.
	Parse request, craft peewee query, return json.
	Easy right?

	docs: https://datatables.net/manual/server-side	

	Will look something like this:
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

	Docs for creating query:
	http://docs.peewee-orm.com/en/latest/peewee/querying.html
	'''

	# defining columns (must match order of datatables)
	columns = [
		'thumbnail_url',
		'title',
		'abstract',
		'identifier'
	]	

	# instantiating a DataTable for the query and table needed
	pdt = PeeweeDT(columns, Record, request.json)

	# returns what is needed by DataTable
	return jsonify(pdt.DToutput)



####################
# RECORD (SR)
####################

# view all records
@oaiglow_app.route("/record/<identifier>", methods=['POST', 'GET'])
def sr(identifier):

	# retrieve single record from database
	record = Record.get(identifier)

	# trigger validation
	record.validate_schematron()

	if record:
		return render_template("record_single.html",localConfig=localConfig, record=record)
	else:
		return render_template("record_single.html",localConfig=localConfig, app_msg="Could not retrieve record from database.")


# update record
@oaiglow_app.route("/record/<identifier>/update", methods=['POST', 'GET'])
def sr_update(identifier):

	# retrieve single record from database
	record = Record.get(identifier)

	if record:

		# update record from OAI-PMH server
		record.update()	

		# trigger validation
		record.validate_schematron()

		return render_template("record_single.html",localConfig=localConfig, record=record, app_msg="Record updated!")

	else:
		return render_template("record_single.html",localConfig=localConfig, app_msg="Could not retrieve record from database.")


@oaiglow_app.route("/record/<identifier>/raw", methods=['POST', 'GET'])
def sr_raw(identifier):

	# retrieve single record from database
	record = Record.get(identifier)

	if record:

		return Response(record.raw, mimetype='text/xml')

	else:

		return jsonify({"status":"no dice"})


@oaiglow_app.route("/record/<identifier>/metadata", methods=['POST', 'GET'])
def sr_metadata(identifier):

	# retrieve single record from database
	record = Record.get(identifier)

	if record:

		return Response(record.metadata_as_string, mimetype='text/xml')

	else:

		return jsonify({"status":"no dice"})


@oaiglow_app.route("/record/<identifier>/validate/schematron", methods=['POST', 'GET'])
def sr_validate_schematron(identifier):

	# retrieve single record from database
	record = Record.get(identifier)
	is_valid, schematron = record.validate_schematron()

	return Response(etree.tostring(schematron.validation_report), mimetype='text/xml')






####################
# REPORTS
####################

