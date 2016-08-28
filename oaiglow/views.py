# views for oaiglow

# flask proper
from flask import render_template, request, session, redirect, make_response, Response

# oaiglow flask app
from oaiglow import oaiglow_app

# localConfig
import localConfig


@oaiglow_app.route("/%s/" % (localConfig.OAIGLOW_APP_PREFIX), methods=['POST', 'GET'])
@oaiglow_app.route("/%s" % (localConfig.OAIGLOW_APP_PREFIX), methods=['POST', 'GET'])
def index():	

	return render_template("index.html", localConfig=localConfig)