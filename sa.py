from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, relationship, Session, sessionmaker
from sqlalchemy import Column, Integer, Text, String, ForeignKey
from sqlalchemy.pool import NullPool


Base = declarative_base()

class Artists(Base):
    __tablename__ = "artists"
    id = Column(Integer, primary_key=True)
    name = Column(String,)
    songs = relationship("Songs", back_populates="artist")


class Songs(Base):
    __tablename__ = "songs"
    id = Column(Integer, primary_key=True)
    name = Column(String,)
    lyrics = Column(Text,)
    artist_id = Column(Integer, ForeignKey("artists.id"), nullable=False)
    artist = relationship("Artists", back_populates="songs")


def get_engine():
    return create_engine("postgresql+psycopg2:///lyrics", )


def session():
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()


def create_tables(engine):
    Base.metadata.create_all(engine)

def drop_all_table(engine):
    Base.metadata.drop_all(bind=engine, )

def initdb():
    engine = get_engine()
    drop_all_table(engine)
    create_tables(engine)


def add_artist(session: Session, artist_name) -> Artists:
    artist = Artists(name=artist_name)
    session.add(artist)
    session.commit()
    session.refresh(artist)
    return artist


def add_song(session: Session, song_name, lyrics, artist):
    song = Songs(name=song_name, lyrics=lyrics, artist=artist)
    session.add(song)
    session.commit()

def get_artists(session: Session):
    return session.query(Artists)

def get_songs_by_artist_id(session: Session, id: int):
    return session.query(Songs).filter(Songs.artist_id==id)

def get_lyrics(session, id: int):
    enginelyrics = session.query(Songs).filter(Songs.id==id).first().lyrics
    return lyrics.split('\n')
