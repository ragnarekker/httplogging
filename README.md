http-logging
============

A simple tool for logging html statuscode and respondstime from a url. In this case the url is a list of keys used in regObs, thus the looging is intended to watch out for downtime on https://api.nve.no/hydrology/regobs/webapi/ which is esentila for the regObs app to work.

The script saves to a sqllite database and is intended to run as a sheduled task. The database i one table generated with: CREATE TABLE "up_time" ("Datetime" DATETIME, "html_code" INTEGER, "req_time" FLOAT, "log_who" TEXT) Some info I found useful on sqllite: http://zetcode.com/db/sqlitepythontutorial/

Output is a select from database and save to file.

Example of the script running on a 15min sheduled task can be seen on http://ragnar.pythonanywhere.com/logs/webapi.log



