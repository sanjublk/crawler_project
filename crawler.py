import argparse
import logging
import os

from bs4 import BeautifulSoup
import requests

logger = None


def generate_name(name: str) -> str:
    '''returns a new string after replacing undesired chars with '-' '''
    char_to_replace = ['/', ' ']
    for char in char_to_replace:
        name = name.replace(char, '-')
    return name.lower()

def parse_args():
    parser = argparse.ArgumentParser(description="Web crawler")
    parser.add_argument(
        "-d", "--debug", help="Enable debug logging", action="store_true"
    )
    parser.add_argument(
        "-c", "--count", type=int, help="Number of artists and songs to crawl", default=2
    )
    parser.add_argument(
       "-u", "--url", type=str, help="Base url for artist list", default= "https://www.songlyrics.com/top-artists-lyrics.html"
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


def get_artists(base: str, count: int=2) -> dict:
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
    for heading in headings[0:count]:
        artists[heading.text] = heading.a["href"]
    return artists


def get_song_list(url: str, count: int=2) -> dict:
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
    for link in links[0:count]:
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
    '''downloads song lyrics into artist directory inside given download_dir'''
    artists = get_artists("https://www.songlyrics.com/top-artists-lyrics.html", count)
    
    for artist, url in artists.items():
        song_list = get_song_list(url, count)
        for song, url in  song_list.items():
            artist_name = generate_name(artist)
            os.makedirs(os.path.join(download_dir, artist_name), exist_ok=True)
            song_name = generate_name(song)
            with open(os.path.join(download_dir, artist_name, f'{song_name}.txt'), 'w') as f:
                byte_count = f.write(get_lyrics(url))
                if byte_count < 5:
                    logger.warn(' %s too small', str(os.path.join(download_dir, artist_name, f'{song_name}.txt')))




def main():
    args = parse_args()
    if args.debug:
        configure_logging()
    else:
        configure_logging(logging.INFO)

    download_lyrics('artists', args.count, args.url) 
if __name__ == "__main__":
    main()
