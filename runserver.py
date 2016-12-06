
# twisted imports
from twisted.web.wsgi import WSGIResource
from twisted.web.server import Site
from twisted.internet import reactor, defer
from twisted.internet.task import deferLater
from twisted.web.server import NOT_DONE_YET
from twisted.web import server, resource
from twisted.python import log

# oaiglow imports
from oaiglow import oaiglow_app

# localConfig
import localConfig
from localConfig import logging

# general imports

# WSUDOR_API_app
oaiglow_resource = WSGIResource(reactor, reactor.getThreadPool(), oaiglow_app)
oaiglow_site = Site(oaiglow_resource)

if __name__ == '__main__':

	# main oaiglow app
	logging.info("starting oaiglow app at :%d, /%s..." % (localConfig.OAIGLOW_APP_PORT, localConfig.OAIGLOW_APP_PREFIX))
	reactor.listenTCP( localConfig.OAIGLOW_APP_PORT, oaiglow_site )

	logging.info('''
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

	logging.info('oaiglow started')

	reactor.run()
