# todo

* database
 * when starting app, confirm database connection is valid

* build out harvesting of records
 * static files are indexing well, focus on iterating over sickle results
 * poll background job?
  * celery?  anything more lightweight?
 * sockets?

* single item page
 * DPLA preview?

* utilities / helper functions
 * consider moving reusable functions from `console` to `utilities.py` file?
 * organizing as static methods for class?
  * e.g. `tableWipe()` for the `Server` class, etc.

* content-type negotiation for single record API routes?

* rollbacks
 * harvesting
 * single record updates