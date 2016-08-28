# oaiglow console

import logging
logging.basicConfig(level=logging.DEBUG)

import localConfig
from oaiglow.models import Server

# fire sickle server instance
logging.debug('firing server instance...')
server = Server()

# test identifiers
logging.debug('loading test identifiers...')
test_records = [ server.get_record(ident) for ident in localConfig.TEST_IDENTIFIERS ]
cfai_example = test_records[0]