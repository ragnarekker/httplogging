#!/usr/bin/python3.5
# -*- coding: utf-8 -*-
import sys as sys
import os as os

__author__ = 'ragnarekker'
log_ref = 'setenvironment.py:'

if 'linux' in sys.platform:
    project_folder      = '/home/ragnar/httplogging/'
    project_log         = project_folder + 'httplogging/logs/'
    db_location         = project_folder + 'httplogging/database/'
    output_log          = '/home/ragnar/BottleSite/logs/'
    plot_folder         = '/home/ragnar/BottleSite/images/httplogplots/'

elif 'darwin' in sys.platform:
    project_folder      = '/Users/ragnarekker/Dropbox/Kode/Python/httplogging/'
    project_log         = project_folder + 'httplogging/logs/'
    db_location         = project_folder + 'httplogging/database/'
    output_log          = project_folder + 'output/'
    plot_folder         = output_log

elif 'win32' in sys.platform:
    project_folder      = 'C:\\Users\\raek\\Dropbox\\Kode\\Python\\httplogging\\'
    project_log         = project_folder + 'httplogging\\logs\\'
    db_location         = project_folder + 'httplogging\\database\\'
    output_log          = project_folder + 'output\\'
    plot_folder         = output_log

else:
    print('{0} The current operating system is not supported: {1}'.format(log_ref, sys.platform))
    project_folder      = None
    project_log         = None
    db_location         = None
    output_log          = None
    plot_folder         = None

if project_folder:
    try:
        # If log folder doesnt exist, make it.
        if not os.path.exists(project_log):
            os.makedirs(project_log)
        if not os.path.exists(db_location):
            os.makedirs(db_location)
        if not os.path.exists(output_log):
            os.makedirs(output_log)
        if not os.path.exists(plot_folder):
            os.makedirs(plot_folder)
    except:
        error_msg = sys.exc_info()[0]
        print('{} Error creating folders: {}.'.format(log_ref, error_msg))