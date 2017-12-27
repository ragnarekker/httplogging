#!/usr/bin/python3.5
# -*- coding: utf-8 -*-
from httplogging import logthings as lt

__author__ = 'ragnarekker'

lt.log_chartserver(parameters=['sdfsw', 'tm', 'sd'], write_to_file=True, make_plot=True)
lt.log_gts(parameters=['sdfsw', 'tm', 'sd'], write_to_file=True, make_plot=True)
lt.log_getobservationswithinradius(write_to_file=True)
lt.log_kdvelements(write_to_file=True)
