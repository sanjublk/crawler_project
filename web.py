from flask import Flask, render_template, json, jsonify
from flask_sqlalchemy import SQLAlchemy
# import sa

app = Flask('crawler')
# session = sa.session()
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///lyrics'
app.config['JSON_SORT_KEYS'] = False
db = SQLAlchemy(app)

class Artists(db.Model):
    __tablename__ = "artists"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String,)
    songs = db.relationship("Songs", back_populates="artist")

    def __repr__(self):
        return f"Artists('{self.name}')"

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class Songs(db.Model):
    __tablename__ = "songs"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String,)
    lyrics = db.Column(db.Text,)
    artist_id = db.Column(db.Integer, db.ForeignKey("artists.id"), nullable=False)
    artist = db.relationship("Artists", back_populates="songs")

    def __repr__(self):
        return f"Songs('{self.name}')"

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


@app.route('/')
def index():
    # artists = sa.get_artists(session)
    artists = Artists.query.all()
    # return jsonify([artist.as_dict() for artist in artists])
    return render_template('index.html', artists=artists)


@app.route('/artist/<int:artist_id>')
def artist(artist_id):
    # songs = sa.get_songs_by_artist_id(session, artist_id)
    artist_name = Artists.query.get(artist_id).name
    songs = Artists.query.get(artist_id).songs
    # return jsonify([song.as_dict() for song in songs])
    return render_template('artist.html', songs=songs, artist_name=artist_name)


@app.route('/song/<int:song_id>')
def song(song_id):
    # lyrics = sa.get_lyrics(session, song_id)
    song = Songs.query.get(song_id)
    song_name = song.name
    lyrics = song.lyrics
    lyrics = lyrics.replace('\n', '<br>')
    # return jsonify({'name': song_name, 'lyrics': lyrics}, )
    return render_template('song.html', lyrics=lyrics, song_name=song_name, artist=song.artist)




