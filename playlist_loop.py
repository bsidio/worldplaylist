# -*- coding: utf-8 -*-

import time
import sqlite3
from serverutils import conf_reader, create_tables

SQLITE, GOOGLE = conf_reader() # load configuration

'''
 -- Sqlite configuration
'''
conn = sqlite3.connect(SQLITE['db'], isolation_level=None, detect_types=sqlite3.PARSE_DECLTYPES)
cur = conn.cursor()
create_tables(cur, SQLITE)

'''
 -- Playlist loop
'''
def loop():
    rep = cur.execute("SELECT VideoId, DurationSeconds FROM " + SQLITE['musictable'] + " ORDER BY Datetime LIMIT 1 ")
    '''
    Traceback (most recent call last):
  File "playlist_loop.py", line 41, in <module>
    while True: loop() # infinite loop
  File "playlist_loop.py", line 21, in loop
    video_id, duration_seconds = rep.fetchone()
TypeError: 'NoneType' object is not iterable
    '''
    # TODO: need to test if rep empty
    video_id, duration_seconds = rep.fetchone()
    print video_id, duration_seconds
    # seconds time loop procedure
    t0 = time.time()
    t1 = int(time.time() - t0)
    t_tmp = t1
    while t1 < duration_seconds:
        t1 = int(time.time() - t0)
        if t1 != t_tmp: # update every seconds
            cur.execute("UPDATE " + SQLITE['seektable'] + " SET Seconds = ? WHERE Id = ?", (t1, 1))
            print t1
            t_tmp = t1
        if t1 >= duration_seconds:
            print 'Delete song'
            cur.execute("DELETE FROM " + SQLITE['musictable'] + " WHERE VideoId = ? ", (video_id,))
            break

'''
 -- Main
'''
if __name__ == '__main__':
    while True: loop() # infinite loop
