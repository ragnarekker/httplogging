__author__ = 'ragnarekker'
# -*- coding: utf-8 -*-

import requests
import json
import datetime
import os.path
import sqlite3 as db
from requests.exceptions import ConnectionError

path_db = 'Logging/'
path_logfile = 'Logging/'
#path_logfile = 'mysite/logs/'  # location on ragnar.pythonanywhere.com

def get_kdvRepositories(kdv):
    """
    :param kdv: respondse from a request for KDVElements from regObs-WebAPI
    :return:    all KDV elements listed neat in a dictionary
    """

    kdv = kdv.json()                    # the request returns a json
    kdv = kdv['Data'].encode('utf-8')   # pick Data key from dictionary and encode
    kdv = json.loads(kdv)               # load the json into a dictionary again

    return kdv['KdvRepositories']

def write_logfile(request_datetime, responds_status_code, responds_time, logfile):
    """

    :param request_datetime:
    :param responds_status_code:
    :param responds_time:
    :param logfile:
    :return:
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

def write_database(request_datetime, responds_status_code, responds_time, log_who, databasefile):
    """
    Find help on http://zetcode.com/db/sqlitepythontutorial/

    :param request_datetime:
    :param responds_status_code:
    :param responds_time:
    :param log_who:
    :param databasefile:
    :return:
    """

    con = db.connect(databasefile)
    data = (request_datetime, responds_status_code, responds_time, log_who)

    with con:
        cur = con.cursor()
        cur.execute('INSERT INTO up_time VALUES (?,?,?,?)', data)

def database2file(databasefile, filename , sqlquery):
    """

    :param databasefile:
    :param filename:
    :param sqlquery:
    :return:
    """

    import csv
    con = db.connect(databasefile)

    with con:
        cur = con.cursor()
        data = cur.execute(sqlquery)

        with open(filename, 'wb') as f:
            writer = csv.writer(f, delimiter='\t')
            writer.writerow(['Datetime (Server is UTC0)', 'Status', 'Elapsed s', 'Who is logged?'])
            writer.writerows(data)

def database2console(databasefile, sqlquery):
    """

    :param databasefile:
    :param sqlquery:
    :return:
    """

    con = db.connect(databasefile)

    with con:
        cur = con.cursor()
        cur.execute(sqlquery)

        rows = cur.fetchall()

        for row in rows:
            print row


if __name__ == '__main__':

    # Sett the variables to timeout-values. If we dont have timeout they will be overwritten.
    responds_status_code = 503
    responds_time = 15.

    # http://stackoverflow.com/questions/21407147/python-requests-exception-type-connectionerror-try-except-does-not-work
    # Get what Im logging
    url = "https://api.nve.no/hydrology/regobs/webapi/kdvelements"

    try:
        kdv = requests.get(url, timeout=15.)
        responds_status_code = kdv.status_code
        responds_time = kdv.elapsed.microseconds/1000000.       # convert microseconds to seconds
    except ConnectionError as e:
        pass
    finally:
        request_datetime = datetime.datetime.now()
        request_datetime = request_datetime.replace(microsecond=0)  # remove microseconds
        log_who = url
        log_who = log_who.replace('http://', '')
        log_who = log_who.replace('https://', '')


        # Write results to database or file
        logfile = '{0}webapi.log'.format(path_logfile)
        databasefile = '{0}logging.sqlite'.format(path_db)

        # write_logfile(request_datetime, responds_status_code, responds_time, logfile)
        write_database(request_datetime, responds_status_code, responds_time, log_who, databasefile)

        # Look up data
        sqlquery = "SELECT * FROM up_time order by Datetime desc"

        # database2console(databasefile, sqlquery)
        database2file(databasefile, logfile, sqlquery)