#!/usr/bin/python3.5
# -*- coding: utf-8 -*-
import datetime as dt
import os as os
from httplogging import setenvironment as se

__author__ = 'ragnarekker'


def log_and_print(message, file_name_prefix='httplogging', file_folder=se.project_log, print_it=False, log_it=True):
    """For logging and printing this method does both.

    :param message:             [string] what to print and/or log
    :param file_name_prefix:    [string] Prefix for log file
    :param file_folder:         [string] Folder to save log files
    :param print_it:            [bool] If true message will be printed to screen (default False)
    :param log_it:              [bool] If false, message will not be logged (default True)
    """

    time_and_message = '{:%H:%M}: '.format(dt.datetime.now().time()) + message
    time_and_message.encode('utf-8')

    if print_it:
        print(time_and_message)

    if log_it:

        # If log folder doesnt exist, make it.
        if not os.path.exists(se.project_log):
            os.makedirs(se.project_log)

        file_name = '{0}{1}_{2}.log'.format(file_folder, file_name_prefix, dt.date.today())
        with open(file_name, 'a', encoding='utf-8') as f:
            f.write(time_and_message + '\n')
