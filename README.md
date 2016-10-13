# oaiglow

## Overview
Utility to harvest and visualize OAI-PMH feeds, with a specific focus on the [DPLA](http://dp.la).

General approach is:
* harvest records from OAI-PMH server, store in database
* provide API access to sets and single records, with funtionality such as:
 * XSLT transformations
 * DPLA single record preview
 * schematron validation


## Installation
* Install dev tools for python3:
<pre><code>sudo apt-get install python3-dev</code></pre> 
* Create python3, virtual environment:
<pre><code>mkvirtualenv --python=/usr/bin/python3 oaiglow
\# depending on how you manage virtual environments, confirm using 'oaiglow' virtualenv</pre></code>

* Install requirements:
<pre><code>pip3 install -r requirements.txt</code></pre>

* Create `localConfig.py` from `localConfig.py.template` and configure

## Run
`./runserver.sh`


## Console
Often, the console is a handy place for maintenence and debugging.  Here are some inroads for working with the API and database.

Start console with some preliminary loading:
<pre><code>./console.sh</code></pre>

Grab harvested record from DB:
<pre><code>record = Record.get('[LONG OAI IDENTIFIER]')</code></pre>

More to come...



