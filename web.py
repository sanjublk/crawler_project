from flask import Flask, render_template, json, jsonify, url_for
from flask_sqlalchemy import SQLAlchemy
import flask_accept
# import sa

app = Flask('crawler')
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
@flask_accept.accept('text/html')
def song(song_id):
    
    song = Songs.query.get(song_id)
    previous_id = song_id
    lyrics = song.lyrics
    # songs = song.artist.songs.order_by("id desc")
    previous, next_ = get_prev_next(song_id, song.artist.songs)
    return render_template(
        'song.html',
        lyrics=lyrics,
        song_name=song.name,
        artist=song.artist,
        songs=song.artist.songs,
        song_id=song_id,
        previous_song_id = previous,
        next_song_id = next_
        )
    # lyrics = sa.get_lyrics(session, song_id)
    # songs = Songs.query.all()
    # return jsonify({'name': song_name, 'lyrics': lyrics}, )


@song.support('application/json')
def song_json(song_id):
    song = Songs.query.get(song_id)
    prev, next_ = get_prev_next(song.id, song.artist.songs)
    return jsonify(
        {'id':song.id,
        'name': song.name, 
        'lyrics': song.lyrics,
        'previous': prev, 
        'next': next_}
        )


@app.route('/lyrics/<int:song_id>')
def lyrics(song_id):
    song = Songs.query.get(song_id)
    prev, next_ = get_prev_next(song.id, song.artist.songs)
    return jsonify(
        {'id':song.id,
        'name': song.name, 
        'lyrics': song.lyrics,
        'previous': prev, 
        'next': next_}
        )



# def get_prev_next(id, songs):
#     print("songs[0]: ", songs[0].id)
#     print("id: ", id)
#     if songs[0].id == id:
#         return None, songs[1].id
#     elif songs[-1].id == id:
#         return songs[-2].id, None
#     else:
#         for index, song in enumerate(songs):
#             if song.id == id:
#                 previous, next_ = songs[index-1].id, songs[index+1].id
#         return previous, next_    


def get_prev_next(id, songs):
    current_index = None
    for index, song in enumerate(songs):
        if song.id == id:
            current_index = index

    if current_index == 0:
        print(None, songs[current_index+1].id)
        return None, songs[current_index+1].id
    elif current_index == len(songs) - 1:
        print(songs[current_index - 1].id, None)
        return songs[current_index - 1].id, None
    else:
        print(songs[current_index-1].id, songs[current_index+1].id)
        return songs[current_index-1].id, songs[current_index+1].id
 