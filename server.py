# -*- coding: utf-8 -*-

import flask
import sqlite3
import requests
import datetime
from serverutils import conf_reader, crossdomain, good_duration, duration_seconds

SQLITE, GOOGLE = conf_reader() # load configuration

'''
 -- Flask configuration
'''
APP_PORT = 8000
app = flask.Flask(__name__, static_url_path='')

'''
 -- Sqlite configuration
'''
conn = sqlite3.connect(SQLITE['db'], isolation_level=None, detect_types=sqlite3.PARSE_DECLTYPES)
cur = conn.cursor()

'''
 -- Routes
'''
@app.route('/')
@crossdomain(origin='*')
def dashboard():
    return app.send_static_file('index.html')

@app.route('/api/musicinfo/<music_id>', methods=['GET', 'OPTIONS'])
@crossdomain(origin='*')
def music_info_get(music_id):
    url = GOOGLE['endpoint'] + '?part=id,contentDetails,snippet&id=' + music_id + '&key=' + GOOGLE['apikey']
    response = requests.get(url)
    data = response.json()
    item = data.get('items')[0]
    duration = item.get('contentDetails')['duration']
    video_id = item.get('id')
    category_id = item.get('snippet')['categoryId']
    title = item.get('snippet')['title']
    duration_s = duration_seconds(duration)
    # TODO: check category & sensitive content
    good_d = good_duration(duration)
    if good_d: # if song duration is okay
        date = datetime.datetime.now()
        link = 'https://www.youtube.com/watch?v=' + video_id
        # push into the db
        cur.execute("INSERT INTO " + SQLITE['musictable'] + """
            (Datetime,Link,CategoryId,Duration,DurationSeconds,VideoId,Title)
            VALUES (?,?,?,?,?,?,?)""", (date, link, category_id, duration, duration_s, video_id, title))
        return flask.jsonify({'status': 'ok', 'message': 'Thanks for your contribution :)'}), 200
    else:
        return flask.jsonify({'status': 'error', 'message': 'Sorry, song duration is too long ..'}), 200

@app.route('/api/musics', methods=['GET', 'OPTIONS'])
@crossdomain(origin='*')
def musics_get():
    rep = cur.execute("SELECT * FROM " + SQLITE['musictable'] + " ORDER BY Datetime LIMIT 1")
    music = rep.fetchone()
    d = {
        'id': music[0],
        'datetime': music[1],
        'link': music[2],
        'categoryId': music[3],
        'duration': music[4],
        'durationSeconds': music[5],
        'videoId': music[6],
        'title': music[7]
    }
    return flask.jsonify({'status': 'ok', 'data': d}), 200


@app.route('/api/seektoseconds', methods=['GET', 'OPTIONS'])
@crossdomain(origin='*')
def seek_to_seconds_get():
    cur.execute("SELECT Id, Seconds FROM " + SQLITE['seektable'] + " WHERE Id=1")
    data = cur.fetchone()
    res = 0
    if data:
        res = data[1]
    return flask.jsonify({'status': 'ok', 'data': res}), 200

@app.route('/api/showmusics', methods=['GET', 'OPTIONS'])
@crossdomain(origin='*')
def show_musics_get():
    rep = cur.execute("SELECT * FROM " + SQLITE['musictable'] + " ORDER BY Datetime LIMIT 11")
    musics = rep.fetchall()
    res = list()
    for music in musics[1:]:
        d = {
            'id': music[0],
            'datetime': music[1],
            'link': music[2],
            'categoryId': music[3],
            'duration': music[4],
            'durationSeconds': music[5],
            'videoId': music[6],
            'title': music[7]
        }
        res.append(d)
    return flask.jsonify({'status': 'ok', 'data': res}), 200

'''
 -- Main
'''
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=APP_PORT) # Run flask app
