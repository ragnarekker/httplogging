__author__ = 'ragnarekker'
# -*- coding: utf-8 -*-

import requests
import json
import datetime
import os.path
import sqlite3 as db
from requests.exceptions import ConnectionError
import csv

path_db = 'Logging/'
path_logfile = 'Logging/'
#path_logfile = 'mysite/logs/'  # location on ragnar.pythonanywhere.com

def get_kdvRepositories(kdv):
    """
    Method which takes a raw respondse from regObs-webAPI and parses it as a json, picks out the data and makes a neat
    dictionary of it.

    :param kdv: respondse from a request for KDVElements from regObs-WebAPI
    :return:    all KDV elements listed neat in a dictionary
    """

    kdv = kdv.json()                    # the request returns a json
    kdv = kdv['Data'].encode('utf-8')   # pick Data key from dictionary and encode
    kdv = json.loads(kdv)               # load the json into a dictionary again

    return kdv['KdvRepositories']

def write2logfile(request_datetime, responds_status_code, responds_time, logfile):
    """
    Alternate method to write a logfile not needing the database. The method checks if the logfile exists and creates it
    if not an opens and and a new line last in the file if it does.

    :param request_datetime:        Time of the logging/request.
    :param responds_status_code:    html-statuscode returned when request is requested.
    :param responds_time:           Respondstime on the request.
    :param logfile:                 Path and name to the logfile.

    :return:                        No return variables.
    """

    if os.path.exists(logfile) == False:
        l = open(logfile, 'a')
        l.write('{0}\t{1}\t{2}\n'.format('Date and time   ', 'Status', 'Elapsed s'))
        l.write('{0}\t{1}\t{2}\n'.format(request_datetime.strftime("%Y-%m-%d %H:%M"), responds_status_code , responds_time))
        l.close()
    else:
        l = open(logfile, 'a')
        l.write('{0}\t{1}\t{2}\n'.format(request_datetime.strftime("%Y-%m-%d %H:%M"), responds_status_code , responds_time))
        l.close()

    return

def write2database(request_datetime, responds_status_code, responds_time, log_who, databasefile):
    """
    Writes the result from the query and responds time and html status code til the database.

    The database is a sqllite database with one table generated with:
    CREATE TABLE "up_time" ("Datetime" DATETIME, "html_code" INTEGER, "req_time" FLOAT, "log_who" TEXT)

    Some info I found useful on sqllite: http://zetcode.com/db/sqlitepythontutorial/

    :param request_datetime:        Time of the logging/request.
    :param responds_status_code:    html-status code returned when request is requested.
    :param responds_time:           Responds time on the request.
    :param log_who:                 URL to what is log'ed
    :param databasefile:            Path and name to the database.
    :return:                        No return variables.
    """

    con = db.connect(databasefile)
    data = (request_datetime, responds_status_code, responds_time, log_who)

    with con:
        cur = con.cursor()
        cur.execute('INSERT INTO up_time VALUES (?,?,?,?)', data)

    return

def database2file(databasefile, filename , sqlquery):
    """
    Writes the result from a given sqlquery to a given database to a given file. Uses pythons csv pacages which makes
    the whole thing quite easy.

    :param databasefile:    Path and name to the database.
    :param filename:        Path and name to the output file.
    :param sqlquery:        The sql query to be executed.

    :return:                No return.
    """

    # Connection to database
    con = db.connect(databasefile)

    with con:
        cur = con.cursor()
        data = cur.execute(sqlquery)

        with open(filename, 'wb') as f:
            writer = csv.writer(f, delimiter='\t')
            writer.writerow(['Datetime (Server is UTC0)', 'Status', 'Elapsed s', 'Who is logged?'])
            writer.writerows(data)

    return

def database2console(databasefile, sqlquery):
    """
    Writes the result from a given sqlquery to a given database to the console.

    :param databasefile:    Path and name to the database.
    :param sqlquery:        The sql query to be executed.
    :return:                No return.
    """

    con = db.connect(databasefile)

    with con:
        cur = con.cursor()
        cur.execute(sqlquery)

        rows = cur.fetchall()

        for row in rows:
            print row

def make_request(url, responds_time, key_thingspeak=None, log_entry=None):

    # Set the variables to timeout-values. If we don't have timeout they will be overwritten.
    responds_status_code = 503

    # On the topic of requests and exceptions on stackoverflow:
    # http://stackoverflow.com/questions/21407147/python-requests-exception-type-connectionerror-try-except-does-not-work
    try:
        request = requests.get(url, timeout=responds_time)
        responds_status_code = request.status_code
        responds_time = request.elapsed.microseconds / 1000000.  # convert microseconds to seconds
    except ConnectionError as e:
        pass
    finally:
        request_datetime = datetime.datetime.now()
        request_datetime = request_datetime.replace(microsecond=0)  # remove microseconds
        log_who = url
        log_who = log_who.replace('http://', '')
        log_who = log_who.replace('https://', '')

        # Write results to database or file
        databasefile = '{0}logging.sqlite'.format(path_db)
        write2database(request_datetime, responds_status_code, responds_time, log_who, databasefile)
        # write2logfile(request_datetime, responds_status_code, responds_time, logfile)

        if key_thingspeak != None:
            # Write result to thingspeak.com for graphing on https://thingspeak.com/channels/
            key_thingspeak = "insert_your_thingspeak_key"  # this is a peronalized key from thingspeak.com
            url_thingspeak = "https://api.thingspeak.com/update?key={0}&field1={1}".format(key_thingspeak, responds_status_code)
            requests.get(url_thingspeak)

        if log_entry != None:
            # Look up data and write til logfile
            logfile = '{0}{1}.log'.format(path_logfile, log_entry)
            sqlquery = 'SELECT * FROM up_time where log_who = "{0}"'.format(log_who)
            database2file(databasefile, logfile, sqlquery)
            # database2console(databasefile, sqlquery)

if __name__ == '__main__':

    log_entry = 'kdvelements'                                           # what am I logging?
    url = "https://api.nve.no/hydrology/regobs/webapi/kdvelements"      # URL to what Im logging
    responds_time = 15.                                                 # How long do we wait for a responds?
    key_thingspeak = 'YOUR KEY HERE'                                    # If result is plotted on thingsspeak.com
    make_request(url, responds_time, key_thingspeak=key_thingspeak, log_entry=log_entry)
