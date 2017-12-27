httplogging
============

This is a simple tool for logging html status code and responds time from urls in Varsom. There are methods for logging urls on regObs, chartserver and GTS and on the two latter applications several parameters are logged and received data is compared with requested data.

The script saves results to different tables in a sqllite3 database and is intended to run as a scheduled task. Output is a select from this database and save to text file and optionally a plot.

Example of the script running on a 15min scheduled task can be seen on http://ragnar.pythonanywhere.com/logs/


