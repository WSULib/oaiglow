# todo

* build out harvesting of records
 * static files are indexing well, focus on iterating over sickle results
 * poll background job?
  * celery?  anything more lightweight?
 * sockets?

* add datatables for viewing harvested records

* single item page
 * overview of metadata, thumbnail, etc.
 * DPLA preview?
 * schematron validation?

* utilities / helper functions
 * consider moving reusable functions from `console` to `utilities.py` file?
 * organizing as static methods for class?
  * e.g. `tableWipe()` for the `Server` class, etc.