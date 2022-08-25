-- Adds drops and creates songs, artists table

DROP TABLE IF EXISTS songs;
DROP TABLE IF EXISTS artists;

CREATE TABLE artists (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL);


CREATE TABLE songs (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    artist_id INTEGER references artists(id),
    lyrics TEXT NOT NULL
);

