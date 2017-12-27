#!/usr/bin/python3.5
# -*- coding: utf-8 -*-
import requests as rq
import datetime as dt
import sys as sys
from httplogging import inputoutput as io
from httplogging import setenvironment as se
from httplogging import makelogs as ml

__author__ = 'ragnarekker'


def _make_request_and_log_to_db(log_name, url, max_responds_time, write_to_file=False):
    """

    :param log_name:
    :param url:
    :param max_responds_time:
    :param write_to_file:
    :return:
    """

    # Set the variables to timeout-values. If we don't have timeout they will be overwritten.
    responds_status_code = 503
    responds_time = max_responds_time
    responds_size = 0

    # On the topic of requests and exceptions on stackoverflow:
    # http://stackoverflow.com/questions/21407147/python-requests-exception-type-connectionerror-try-except-does-not-work
    try:
        request = rq.get(url, timeout=max_responds_time)
        responds_size = len(request.content)
        responds_status_code = request.status_code
        responds_time = request.elapsed.microseconds / 1000000.  # convert microseconds to seconds

    except ConnectionError as e:
        pass

    finally:
        date_and_time = dt.datetime.now().replace(microsecond=0)  # remove microseconds
        log_who = url
        #log_who = log_who.replace('http://', '')
        #log_who = log_who.replace('https://', '')

        # Write results to database or file
        database_file = '{0}logging.sqlite'.format(se.db_location)
        io.db_insert_up_time(date_and_time, log_name, responds_status_code, responds_time, responds_size, log_who, database_file)

        if write_to_file:
            # Look up data and write til log file
            file_name = '{0}{1}.log'.format(se.output_log, log_name)
            sql_query = 'SELECT * FROM up_time WHERE log_who_short_name = "{0}" ORDER BY date_and_time DESC LIMIT 672'.format(log_name)
            log_file_header = ['date_and_time (Server is UTC0)', 'log_who_short_name', 'http_code', 'responds_time (s)', 'responds_size (bytes)', 'log_who']
            io.db_to_file(database_file, file_name, sql_query, log_file_header=log_file_header)


def log_kdvelements(write_to_file=False):
    """

    :param write_to_file:
    :return:
    """

    log_name = 'kdvelements'                                           # what am I logging?
    url = "https://api.nve.no/hydrology/regobs/webapi/kdvelements"      # URL to what Im logging
    max_responds_time = 15.                                             # How long do we wait for a responds?
    _make_request_and_log_to_db(log_name, url, max_responds_time, write_to_file=write_to_file)


def log_getobservationswithinradius(write_to_file=False):
    """

    :param write_to_file:
    :return:
    """

    log_name = 'getobservationswithinradius'
    url = 'https://api.nve.no/hydrology/RegObs/webapi/Observations/GetObservationsWithinRadius?latitude=59.844226&longitude=10.42702&range=100000&geohazardId=70&$format=JSON'
    max_responds_time = 15.
    _make_request_and_log_to_db(log_name, url, max_responds_time, write_to_file=write_to_file)


def log_gts(parameters=None, write_to_file=False, make_plot=False):
    """

    :param parameters:
    :param write_to_file:
    :param make_plot
    :return:
    """

    if parameters is None:
        parameters = ['sdfsw', 'tm', 'sd']

    database_file = se.db_location + 'logging.sqlite'

    for parameter in parameters:
        days_requested = 21
        to_date = dt.date.today() + dt.timedelta(days=2)
        from_date = to_date - dt.timedelta(days=(days_requested - 1))
        to_date = to_date.strftime('%Y-%m-%d')  # '20171205'
        from_date = from_date.strftime('%Y-%m-%d')  # '20171213'

        log_time = dt.datetime.now().replace(microsecond=0)  # remove microseconds

        url = 'http://h-web02.nve.no:8080/api/GridTimeSeries/gridtimeserie?' \
              'theme={2}&startdate={0}&enddate={1}&x=111899&y=6730791'\
            .format(from_date, to_date, parameter)

        try:
            response = rq.get(url)
            response_text = response.text
            full_data = response.json()
            data = full_data['Data']

            days_received = len(data)
            http_code = response.status_code
            response_time = response.elapsed.microseconds / 1000000.    # convert microseconds to seconds

        except:
            error_msg = sys.exc_info()[0]
            ml.log_and_print('logthings.py -> log_gts: Error requesting {}. {}'.format(url, error_msg))

            http_code = 0
            response_time = 0
            days_received = 0
            response_text = ''

        io.db_insert_gts_up_time(
            log_time, parameter, http_code, response_time, days_requested, days_received,
            url, response_text, database_file)

    if write_to_file:
        # Look up data and write til log file
        file_name = '{0}{1}.log'.format(se.output_log, 'gts')
        sql_query = 'SELECT date_and_time, parameter, http_code, responds_time, days_requested, days_received FROM gts_up_time ORDER BY date_and_time DESC'
        log_file_header = ['date_and_time', 'parameter', 'http_code', 'responds_time', 'days_requested', 'days_received']
        io.db_to_file(database_file, file_name, sql_query, log_file_header=log_file_header)

    if make_plot:
        sql_query = 'SELECT date_and_time, parameter, http_code, responds_time, days_requested, days_received FROM gts_up_time ORDER BY date_and_time DESC'
        io.db_to_plot_chartserver_and_gts(database_file, sql_query, parameters, file_identifyer='gts')

    return


def log_chartserver(parameters=None, write_to_file=False, make_plot=False):
    """

    :param parameters:
    :param write_to_file:
    :param make_plot
    :return:
    """

    if parameters is None:
        parameters = ['sdfsw', 'tm', 'sd']

    database_file = se.db_location + 'logging.sqlite'

    for parameter in parameters:
        days_requested = 21
        to_date = dt.date.today() + dt.timedelta(days=2)
        from_date = to_date - dt.timedelta(days=(days_requested-1))
        to_date = to_date.strftime('%Y%m%d')                # '20171205'
        from_date = from_date.strftime('%Y%m%d')            # '20171213'

        log_time = dt.datetime.now().replace(microsecond=0)  # remove microseconds

        url = 'http://h-web01.nve.no/chartserver/ShowData.aspx?req=getchart&ver=1.0&vfmt=text' \
              '&time={0}T0600;{1}T0600' \
              '&chs=10x10&lang=no&chlf=desc&chsl=0;+0&chhl=2|0|2&timeo=-06:00&app=3d' \
              '&chd=ds=hgts,da=29,id=111899;6730791;{2},cht=line,mth=inst&nocache=0.1597993119329173'\
            .format(from_date, to_date, parameter)

        try:
            response = rq.get(url)

            data = response.text
            data_in_lines = data.split('<br />')
            data_in_lines = list(filter(None, data_in_lines))           # remove empty lines

            # check if data is there
            days_without_data = 0
            for i, d in enumerate(data_in_lines):
                row = d.split(', ')
                row = [r.strip() for r in row]                          # remove space at end of rowstring
                row = list(filter(None, row))
                data_in_lines.pop(i)                                    # remove the string
                data_in_lines.insert(i, row)                            # and now add the list
                if len(row) < 2:
                    days_without_data += 1

            http_code = response.status_code
            response_time = response.elapsed.microseconds / 1000000.    # convert microseconds to seconds
            if 'Ingen data' in data:
                days_received = 0
            else:
                days_received = days_requested - days_without_data

        except:
            error_msg = sys.exc_info()[0]
            ml.log_and_print('logthings.py -> log_chartserver: Error requesting {}. {}'.format(url, error_msg))

            http_code = 0
            response_time = 0
            days_received = 0
            data = ''

        io.db_insert_chartserver_up_time(
            log_time, parameter, http_code, response_time, days_requested, days_received,
            url, data, database_file)

    if write_to_file:
        # Look up data and write til log file
        file_name = '{0}{1}.log'.format(se.output_log, 'chartserver')
        sql_query = 'SELECT date_and_time, parameter, http_code, responds_time, days_requested, days_received FROM chartserver_up_time ORDER BY date_and_time DESC'
        log_file_header = ['date_and_time', 'parameter', 'http_code', 'responds_time', 'days_requested', 'days_received']
        io.db_to_file(database_file, file_name, sql_query, log_file_header=log_file_header)

    if make_plot:
        sql_query = 'SELECT date_and_time, parameter, http_code, responds_time, days_requested, days_received FROM chartserver_up_time ORDER BY date_and_time DESC'
        io.db_to_plot_chartserver_and_gts(database_file, sql_query, parameters, file_identifyer='chartserver')


if __name__ == '__main__':

    # log_chartserver()
    # log_getobservationswithinradius()
    # log_kdvelements()
    log_gts(write_to_file=True)