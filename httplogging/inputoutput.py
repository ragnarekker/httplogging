#!/usr/bin/python3.5
# -*- coding: utf-8 -*-
import os.path
import sqlite3 as db
import csv
import datetime as dt
from matplotlib import pyplot as plt
from httplogging import setenvironment as se

__author__ = 'ragnarekker'


def file_add_up_time(request_datetime, responds_status_code, responds_time, logfile):
    """Alternate method to write a logfile not needing the database. The method checks if the
    logfile exists and creates it if not an opens and and a new line last in the file if it does.

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


def db_insert_up_time(date_and_time, log_who_short_name, http_code, responds_time, responds_size, log_who, database_file):
    """Writes the result from the query and responds time and html status code til the database.

    The sqlite database table is generated with:
    CREATE TABLE "up_time" ("date_and_time" DATETIME, "log_who_short_name" TEXT, "http_code" INTEGER,
                            "responds_time" FLOAT, "responds_size" INTEGER, "log_who" TEXT)

    Some info I found useful on sqllite: http://zetcode.com/db/sqlitepythontutorial/

    :param date_and_time:       Time of the logging/request.
    :param log_who_short_name
    :param http_code:           html-status code returned when request is requested.
    :param responds_time:       Responds time on the request.
    :param responds_size:
    :param log_who:             URL to what is log'ed
    :param database_file:       Path and name to the database.

    :return:                    No return variables.
    """

    con = db.connect(database_file)
    data = (date_and_time, log_who_short_name, http_code, responds_time, responds_size, log_who)

    with con:
        cur = con.cursor()
        cur.execute('INSERT INTO up_time VALUES (?,?,?,?,?,?)', data)


def db_insert_chartserver_up_time(date_and_time, parameter, http_code, responds_time, days_requested, days_received, log_who, responds_text, database_file):
    """

    The sqlite database table is generated with:
    CREATE TABLE "chartserver_up_time" ("date_and_time" DATETIME, "parameter" TEXT, "http_code" INTEGER, "responds_time" FLOAT,
                                        "days_requested" INTEGER, "days_received" INTEGER,
                                        "log_who" TEXT, "responds_text" TEXT)

    :param date_and_time:
    :param parameter:
    :param http_code:
    :param responds_time:
    :param days_requested:
    :param days_received:
    :param log_who:
    :param responds_text:
    :param database_file:

    :return:
    """

    con = db.connect(database_file)
    data = (date_and_time, parameter, http_code, responds_time, days_requested, days_received, log_who, responds_text)

    with con:
        cur = con.cursor()
        cur.execute('INSERT INTO chartserver_up_time VALUES (?,?,?,?,?,?,?,?)', data)


def db_insert_gts_up_time(date_and_time, parameter, http_code, responds_time, days_requested, days_received, log_who, responds_text, database_file):
    """

    The sqlite database table is generated with:
    CREATE TABLE "gts_up_time" ("date_and_time" DATETIME, "parameter" TEXT, "http_code" INTEGER, "responds_time" FLOAT,
                                        "days_requested" INTEGER, "days_received" INTEGER,
                                        "log_who" TEXT, "responds_text" TEXT)

    For terminal work: https://sqlite.org/cli.html

    :param date_and_time:
    :param parameter:
    :param http_code:
    :param responds_time:
    :param days_requested:
    :param days_received:
    :param log_who:
    :param responds_text:
    :param database_file:

    :return:
    """

    con = db.connect(database_file)
    data = (date_and_time, parameter, http_code, responds_time, days_requested, days_received, log_who, responds_text)

    with con:
        cur = con.cursor()
        cur.execute('INSERT INTO gts_up_time VALUES (?,?,?,?,?,?,?,?)', data)


def db_to_file(database_file, log_file_name, sql_query, log_file_header=False):
    """Writes the result from a given sqlquery to a given database to a given file.
    Uses pythons csv pacages which makes the whole thing quite easy.

    :param databasefile:    Path and name to the database.
    :param filename:        Path and name to the output file.
    :param sqlquery:        The sql query to be executed.

    :return:                No return.
    """

    # Connection to database
    con = db.connect(database_file)

    with con:
        cur = con.cursor()
        data = cur.execute(sql_query)

        with open(log_file_name, 'w', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter='\t',  lineterminator='\n')
            if log_file_header:
                writer.writerow(log_file_header)
            writer.writerows(data)


def db_to_console(database_file, sql_query):
    """Writes the result from a given sql query to a given database to the console.

    :param database_file:    Path and name to the database.
    :param sql_query:        The sql query to be executed.
    """

    con = db.connect(database_file)

    with con:
        cur = con.cursor()
        cur.execute(sql_query)

        rows = cur.fetchall()

        for row in rows:
            print(row)


def db_to_plot_up_time(database_file, sql_query, file_identifyer):
    """

    :param database_file:
    :param sql_query:
    :param file_identifyer:
    :return:
    """

    con = db.connect(database_file)
    con.row_factory = db.Row

    plot_file_name = '{}{}_log.png'.format(se.plot_folder, file_identifyer)
    data = {}

    with con:
        cur = con.cursor()
        cur.execute(sql_query)
        all_rows = cur.fetchall()
        headers = all_rows[0].keys()

        # Make dictionary with column headers as keys and data in list as values
        for i, h in enumerate(headers):
            data[headers[i]] = []

        for row in all_rows:
            data_row = tuple(row)
            for i, d in enumerate(data_row):
                if i == 0:  # fist column is the date time
                    d = dt.datetime.strptime(d, '%Y-%m-%d %H:%M:%S')
                data[headers[i]].append(d)

    fsize = (12, 9)
    plt.figure(figsize=fsize)
    plt.clf()

    plt.suptitle('{} log'.format(file_identifyer), fontsize=28)

    # http code
    plt.subplot2grid((3, 1), (0, 0), rowspan=1)
    plt.plot(data[headers[0]], data[headers[2]], 'mo')
    plt.ylabel('HTTP code')
    plt.ylim(ymin=-50, ymax=550)

    # responds time
    plt.subplot2grid((3, 1), (1, 0), rowspan=1)
    plt.plot(data[headers[0]], data[headers[3]], color='black')
    plt.ylabel('Responds time [s]')
    plt.ylim(ymin=0,ymax=2)

    # data received in kilo bytes
    plt.subplot2grid((3, 1), (2, 0), rowspan=1)
    if 'kdvelements' in file_identifyer:
        face_color = 'peachpuff'
    elif 'getobservationswithinradius' in file_identifyer:
        face_color = 'pink'
    else:
        face_color = 'lightgray'
    plt.fill_between(data[headers[0]], 0, data[headers[4]], facecolor=face_color)
    plt.ylabel('Received data [Bytes]')

    plt.savefig(plot_file_name)
    plt.close()


def db_to_plot_chartserver_and_gts(database_file, sql_query, parameters, file_identifyer='chartserver'):
    """Plots three subplots with http responds, responds time and an area plot for how many days of data
    is recieved.

    :param database_file:       [string] full path to the sqlite database containing the data.
    :param sql_query:           [string] The query to the sqlite database used to receive the data sett for the plot.
    :param parameters:          [list of strings] Eg. ['sdfsw', 'tm', 'sd']
    :param file_identifyer:     [string] 'chartserver' or 'gts'
    :return:
    """

    con = db.connect(database_file)
    con.row_factory = db.Row

    for p in parameters:

        plot_file_name = '{}{}_{}_log.png'.format(se.plot_folder, file_identifyer, p)
        data = {}

        with con:
            cur = con.cursor()
            cur.execute(sql_query)
            all_rows = cur.fetchall()
            headers = all_rows[0].keys()

            # Make dictionary with column headers as keys and data in list as values
            for i, h in enumerate(headers):
                data[headers[i]] = []

            for row in all_rows:
                data_row = tuple(row)
                if data_row[1] == p:
                    for i, d in enumerate(data_row):
                        if i == 0: # fist column is the date time
                            d = dt.datetime.strptime(d, '%Y-%m-%d %H:%M:%S')
                        data[headers[i]].append(d)

        fsize = (12, 9)
        plt.figure(figsize=fsize)
        plt.clf()

        plt.suptitle('{} - {} log'.format(p, file_identifyer), fontsize=28)

        # http code
        plt.subplot2grid((3, 1), (0, 0), rowspan=1)
        plt.plot(data[headers[0]], data[headers[2]], 'mo')
        plt.ylabel('HTTP code')
        plt.ylim(ymin=-50, ymax=550)

        # responds time
        plt.subplot2grid((3, 1), (1, 0), rowspan=1)
        plt.plot(data[headers[0]], data[headers[3]], color='black')
        plt.ylabel('Responds time [s]')

        # data requested vs received
        plt.subplot2grid((3, 1), (2, 0), rowspan=1)
        if 'gts' in file_identifyer:
            face_color = 'turquoise'
        else:
            face_color = 'skyblue'
        plt.fill_between(data[headers[0]], 0, data[headers[5]], facecolor=face_color)
        plt.ylabel('Received data [#]')

        plt.savefig(plot_file_name)
        plt.close()


if __name__ == '__main__':

    database_file = se.db_location + 'logging.sqlite'
    sql_query = 'SELECT date_and_time, parameter, http_code, responds_time, days_requested, days_received FROM chartserver_up_time ORDER BY date_and_time DESC'
    parameters = ['sdfsw', 'tm', 'sd']
    db_to_plot_chartserver_and_gts(database_file, sql_query, parameters)
