import argparse
import logging
import os

from bs4 import BeautifulSoup
import requests

import db
import sa
import web

logger = None


def generate_name(name: str) -> str:
    """returns a new string after replacing undesired chars with '-'"""
    char_to_replace = ["/", " "]
    for char in char_to_replace:
        name = name.replace(char, "-")
    return name.lower()


def parse_args():
    parser = argparse.ArgumentParser(description="Web crawler", add_help=True)
    parser.add_argument(
        "-d", "--debug", help="Enable debug logging", action="store_true"
    )
    sub_commands = parser.add_subparsers(help="sub-commands", dest="command")
    initdb_parser = sub_commands.add_parser('initdb', help='initiate database', )
    crawl_parser = sub_commands.add_parser('crawl', help='start crawling')
    web_parser = sub_commands.add_parser('web', help='starting web server')
    crawl_parser.add_argument('-c', '--count', type=int, help='Number of artists and songs to crawl', default=2)
    crawl_parser.add_argument('-ac', '--artists-count', type=int, help='specify number of artists to crawl', default=2)
    crawl_parser.add_argument('-sc', '--songs-count', type=int, help='specify number of songs to crawl', default=2)
    crawl_parser.add_argument('-u', '--url', help='Url for artist list', default='https://www.songlyrics.com/top-artists-lyrics.html')
    return parser.parse_args()


def configure_logging(level=logging.INFO):
    global logger
    logger = logging.getLogger("crawler")
    logger.setLevel(level)
    screen_handler = logging.StreamHandler()
    screen_handler.setLevel(level)
    formatter = logging.Formatter(
        "[%(levelname)s] : %(filename)s(%(lineno)d) : %(message)s"
    )
    screen_handler.setFormatter(formatter)
    logger.addHandler(screen_handler)


def get_artists(base: str, artists_count: int) -> dict:
    """returns a dictionary of artists with the url to their song list"""
    artists = {}
    logger.debug(f"requesting {base} ...")
    res = requests.get(base)
    logger.debug(f"status code: {res.status_code}")
    soup = BeautifulSoup(res.content, "lxml")
    tracklist = soup.find("table", attrs={"class": "tracklist"})
    headings = tracklist.find_all("h3")
    if not headings:
        logger.debug("could'nt parse headings successfully")

    if artists_count > len(headings):
        artists_count = len(headings)
        logger.debug('count greater than total no. of artists\nreset to maximum available numbers')


    for heading in headings[0:artists_count]:
        artists[heading.text] = heading.a["href"]
    return artists


def get_song_list(url: str, songs_count) -> dict:
    """returns a dictionary of songs with the url to the song lyrics"""
    songs = {}
    logger.debug(f"requesting {url} ...")
    res = requests.get(url)
    logger.debug(f"status code: {res.status_code}")
    soup = BeautifulSoup(res.content, "lxml")
    tracklist = soup.find("table", attrs={"class": "tracklist"})
    links = tracklist.find_all("a")
    if not links:
        logger.debug("could'nt parse headings successfully")
    if songs_count > len(links):
        songs_count = len(links)
        logger.debug('count greater than total no. of songs available\nreset to maximum available numbers')
    for link in links[0:songs_count]:
        songs[link.text] = link["href"]
    return songs


def get_lyrics(url: str) -> str:
    "returns song lyrics parsed from the given url"
    logger.debug(f"requesting {url} ...")
    res = requests.get(url)
    logger.debug(f"status code: {res.status_code}")
    soup = BeautifulSoup(res.content, "lxml")
    lyrics = soup.find("p", attrs={"id": "songLyricsDiv"})
    if lyrics:
        logger.debug("lyrics parsed successfully")
    else:
        logger.debug("could'nt parse lyrics successfully")
    return lyrics.text


def download_lyrics(download_dir: str, count: int, base_url: str):
    """downloads song lyrics into artist directory inside given download_dir"""
    artists = get_artists("https://www.songlyrics.com/top-artists-lyrics.html", count)

    for artist, url in artists.items():
        song_list = get_song_list(url, count)
        for song, url in song_list.items():
            artist_name = generate_name(artist)
            os.makedirs(os.path.join(download_dir, artist_name), exist_ok=True)
            song_name = generate_name(song)
            with open(
                os.path.join(download_dir, artist_name, f"{song_name}.txt"), "w"
            ) as f:
                byte_count = f.write(get_lyrics(url))
                if byte_count < 5:
                    logger.warn(
                        " %s too small",
                        str(
                            os.path.join(download_dir, artist_name, f"{song_name}.txt")
                        ),
                    )

def insert_lyrics_to_database(url, artists_count, songs_count):
    artists = get_artists(url, artists_count)
    conn = db.get_connection()
    for artist, url in artists.items():
        song_list = get_song_list(url, songs_count)
        artist_name = generate_name(artist)
        artist_id = db.add_artist(conn, artist_name)
        for song, url in song_list.items():
            song_name = generate_name(song)
            lyrics = get_lyrics(url)
            db.add_song(conn, song_name, artist_id, lyrics)
    conn.close()

def insert_lyrics_to_database_sa(url, artists_count, songs_count):
    artists = get_artists(url, artists_count)
    session = sa.session()
    for artist, url in artists.items():
        song_list = get_song_list(url, songs_count)
        artist_name = generate_name(artist)
        artist = sa.add_artist(session, artist_name)
        for song, url in song_list.items():
            song_name = generate_name(song)
            lyrics = get_lyrics(url)
            sa.add_song(session, song_name, lyrics, artist)
    session.commit()
    session.close()


def main():
    args = parse_args()
    if args.debug:
        configure_logging(logging.DEBUG)
    else:
        configure_logging(logging.INFO)

    if args.command == 'crawl':
        insert_lyrics_to_database_sa(args.url, args.artists_count, args.songs_count)
    
    elif args.command == 'initdb':
        db.initdb()
    
    elif args.command == 'web':
        web.app.run()



if __name__ == "__main__":
    main()
