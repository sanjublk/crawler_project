"""This module contains functions to get a connection from database, add artists to database and add songs to database."""

import psycopg2

def get_connection(dbname='lyrics'):
    """returns connection handler"""
    return psycopg2.connect(f'dbname={dbname}')


def initdb():
    """executes sql commands in init.sql"""
    conn = get_connection()
    with conn.cursor() as curs:
        with open('init.sql') as f:
            curs.execute(f.read())
            conn.commit()
    conn.close()


def add_artist(conn, artist_name):
    """add artist to artists table in database"""
    with conn.cursor() as curs:
        curs.execute('INSERT INTO artists(name) VALUES(%s) returning artists.id', (artist_name,))
        last_id = curs.fetchone()[0]
        conn.commit()
        return last_id


def add_song(conn, song_name, artist_id, lryics):
    """add song to songs table in database"""
    with conn.cursor() as curs:
        curs.execute('INSERT INTO songs(name, artist_id, lyrics) VALUES(%s, %s, %s)', (song_name, artist_id, lryics))
        conn.commit()


def get_artist_songs(conn, artist_id):
    with conn.cursor() as curs:
        curs.execute('SELECT name')
