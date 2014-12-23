__author__ = 'ragnarekker'
# -*- coding: utf-8 -*-

import sqlite3 as lite
import datetime

con = lite.connect('Logging/logging.sqlite')

data = (
           (datetime.datetime.now(), 200, 1.896, "rO webAPI"),
           (datetime.datetime.now(), 404, 0.596, "www.regobs.no")
)

with con:

    cur = con.cursor()
    cur.executemany('INSERT INTO up_time VALUES (?,?,?,?)', data)
