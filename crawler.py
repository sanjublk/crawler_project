import argparse
import logging

from bs4 import BeautifulSoup
import requests

logger = None


def parse_args():
    parser = argparse.ArgumentParser(description="Web crawler")
    parser.add_argument(
        "-d", "--debug", help="Enable debug logging", action="store_true"
    )
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


def get_artists(base):
    """returns a dictionary of artists with the url to their song list"""
    artists = {}
    logger.debug(f"requesting {base} ...")
    res = requests.get(base)
    logger.debug(f"status code: {res.status_code}")
    soup = BeautifulSoup(res.content, "lxml")
    tracklist = soup.find("table", attrs={"class": "tracklist"})
    headings = tracklist.find_all("h3")
    if headings:
        logger.debug("artist list parsed successfully")
    else:
        logger.debug("could'nt parse headings successfully")
    for heading in headings:
        artists[heading.text] = heading.a["href"]
    return artists


def get_song_list(base):
    """returns a dictionary of songs with the url to the song lyrics"""
    songs = {}
    logger.debug(f"requesting {base} ...")
    res = requests.get(base)
    logger.debug(f"status code: {res.status_code}")
    soup = BeautifulSoup(res.content, "lxml")
    tracklist = soup.find("table", attrs={"class": "tracklist"})
    links = tracklist.find_all("a")
    if links:
        logger.debug("song list parsed successfully")
    else:
        logger.debug("could'nt parse headings successfully")
    for link in links:
        songs[link.text] = link["href"]
    return songs


def get_lyrics(base):
    "returns song lyrics parsed from the given url"
    logger.debug(f"requesting {base} ...")
    res = requests.get(base)
    logger.debug(f"status code: {res.status_code}")
    soup = BeautifulSoup(res.content, "lxml")
    lyrics = soup.find("p", attrs={"id": "songLyricsDiv"})
    if lyrics:
        logger.debug("lyrics parsed successfully")
    else:
        logger.debug("could'nt parse lyrics successfully")
    return lyrics.text


def main():
    args = parse_args()
    if args.debug:
        configure_logging(logging.DEBUG)
    else:
        configure_logging(logging.INFO)

    artists = get_artists("https://www.songlyrics.com/top-artists-lyrics.html")


if __name__ == "__main__":
    main()
