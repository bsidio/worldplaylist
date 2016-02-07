# -*- coding: utf-8 -*-

import json
from datetime import timedelta
from flask import make_response, request, current_app
from functools import update_wrapper

'''
Configuration
'''
CONF_FILE = 'conf.json'

def conf_reader():
    with open(CONF_FILE, 'r') as out:
        data = json.load(out)
    sqlite, google = data.get('sqlite'), data.get('google')
    return sqlite, google

'''
Sqlite
'''
def create_tables(cur, SQLITE):
    cur.execute("CREATE TABLE IF NOT EXISTS " + SQLITE['seektable'] + "(Id INT NOT NULL, Seconds INT NOT NULL)")
    cur.execute("DELETE FROM " + SQLITE['seektable'])
    cur.execute("INSERT INTO " + SQLITE['seektable'] + "(Id, Seconds) VALUES (?,?)", (1, 0))
    cur.execute("CREATE TABLE IF NOT EXISTS " + SQLITE['musictable'] + """(
                    Id INT PRIMARY KEY,
                    Datetime TIMESTAMP NOT NULL,
                    Link TEXT NOT NULL,
                    CategoryId TEXT NOT NULL,
                    Duration TEXT NOT NULL,
                    DurationSeconds INT NOT NULL,
                    VideoId TEXT NOT NULL,
                    Title TEXT NOT NULL)""")

'''
Youtube
'''
def good_category(category_id):
    catego = int(category_id)
    if catego == 10 or catego == 24:
        return True
    else:
        return False    

def good_duration(duration):
    d = duration.replace('PT', '')
    if d.find('H') != -1:
      return False
    if d.find('M') != -1:
        minutes = float(d[0:d.index('M')])
        if minutes < 11 and minutes >= 0:
            return True
        else:
            return False
    if d.find('S') != -1:
        return True
    else:
        return False

def duration_seconds(duration):
    d = duration.replace('PT', '')
    minutes = 0.0
    if d.find('H') != -1:
      return 0
    if d.find('M') != -1:
        minutes = float(d[0:d.index('M')])
        d = d.replace(d[0:d.index('M')+1], '')
    d = d.replace('S', '')
    seconds = float(d)
    total = seconds + (60.0 * minutes)
    return total

'''
Flask
'''
def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator
