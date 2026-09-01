# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
import os
import sqlite3
from flask import g

DATABASE = '/data/waveform.db'

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id           INTEGER PRIMARY KEY,
    username     TEXT UNIQUE NOT NULL,
    password     TEXT NOT NULL,
    email        TEXT NOT NULL,
    display_name TEXT NOT NULL,
    is_admin     INTEGER DEFAULT 0,
    bio          TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS artists (
    id    INTEGER PRIMARY KEY,
    name  TEXT NOT NULL,
    genre TEXT NOT NULL,
    bio   TEXT DEFAULT '',
    cover_url TEXT DEFAULT '',
    monthly_listeners INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS albums (
    id        INTEGER PRIMARY KEY,
    artist_id INTEGER NOT NULL,
    title     TEXT NOT NULL,
    year      INTEGER NOT NULL,
    cover_note TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS tracks (
    id            INTEGER PRIMARY KEY,
    album_id      INTEGER NOT NULL,
    title         TEXT NOT NULL,
    duration_sec  INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS playlists (
    id          INTEGER PRIMARY KEY,
    user_id     INTEGER NOT NULL,
    title       TEXT NOT NULL,
    description TEXT DEFAULT '',
    is_private  INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS playlist_tracks (
    id          INTEGER PRIMARY KEY,
    playlist_id INTEGER NOT NULL,
    track_id    INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS royalties (
    id        INTEGER PRIMARY KEY,
    artist_id INTEGER NOT NULL,
    period    TEXT NOT NULL,
    amount    REAL NOT NULL,
    memo      TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS _flags (
    id    INTEGER PRIMARY KEY,
    name  TEXT UNIQUE NOT NULL,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS plays (
    id         INTEGER PRIMARY KEY,
    user_id    INTEGER NOT NULL,
    track_id   INTEGER NOT NULL,
    played_at  TEXT NOT NULL,
    note       TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS follows (
    id         INTEGER PRIMARY KEY,
    user_id    INTEGER NOT NULL,
    artist_id  INTEGER NOT NULL,
    note       TEXT DEFAULT ''
);

INSERT OR IGNORE INTO users VALUES
  (1,'admin','123456789','admin@waveform.local','Admin',1,'Platform admin. Keeper of the founders'' demo vault.'),
  (2,'sasha','sunflower','sasha@example.com','Sasha Reyes',0,'Bedroom pop obsessive. Always looking for the next Marigold Static track.'),
  (3,'devon','skateboard','devon@example.com','Devon Lark',0,'Synthwave at 2am is the only way to code.'),
  (4,'priya','butterfly','priya@example.com','Priya Nair',0,'Dream pop and rainy windows. That''s the whole personality.'),
  (5,'omar','password1','omar@example.com','Omar Faris',0,'Shoegaze forever. Volume knob only goes one way.'),
  (6,'ines','chocolate','ines@example.com','Ines Coto',0,'Ambient producer. I make music for other people''s focus playlists.'),
  (7,'theo','sunshine','theo@example.com','Theo Marsh',0,'Post-punk revivalist. The bass line is the whole song.');

INSERT OR IGNORE INTO artists (id, name, genre, bio, monthly_listeners) VALUES
  (1,'Lena Fairweather','Indie Folk','A Portland-based songwriter known for close-mic''d vocals and a single battered acoustic guitar.',42300),
  (2,'Kilowatt Kids','Synthwave','Two brothers and a wall of vintage analog synths, chasing the sound of a city that never existed.',118700),
  (3,'Marigold Static','Bedroom Pop','Recorded entirely on a laptop in a converted closet. Somehow it sounds bigger than most studio albums.',89450),
  (4,'The Nightbus','Post-Punk','Angular guitars and even more angular opinions. Formed on a delayed night bus in Manchester.',31200),
  (5,'Coral & Ash','Dream Pop','A duo built around reverb, tape hiss, and the space between notes.',56800),
  (6,'Ruedi Voss','Ambient / Lo-fi','Field recordings layered under warm tape loops. Made for studying, sleeping, and staring out of windows.',24100),
  (7,'Static Season','Shoegaze','Walls of distorted guitar with vocals buried just deep enough to feel like a secret.',47900),
  (8,'Vela Winters','Neo-Soul','Warm, unhurried grooves built around a Rhodes piano and a voice that sounds like it''s smiling.',63500),
  (9,'CommonHuman Labs','Unclassifiable','Not a band. Not a label. A community of people who occasionally make noise between finding bugs. If you found this row, you were paying attention.',1337),
  (10,'Paper Moths','Indie Rock','Three chords, four members, and a very strong opinion about vinyl versus streaming.',52200),
  (11,'Glass Weather','Electronic','Modular synth patches built live — no two shows ever sound the same.',77300),
  (12,'Harbor Lights','Folk','Acoustic duo writing songs about small towns and slow mornings.',28900),
  (13,'Nova Static','Synth-Pop','Bright hooks over distorted drum machines. Allegedly named after a broken TV.',94600);

INSERT OR IGNORE INTO albums VALUES
  (1,1,'Low Tide Letters',2024,'Hand-drawn cover, screen-printed in a run of 200.'),
  (2,1,'Porch Light Sessions',2025,'Recorded live on a porch during a thunderstorm.'),
  (3,2,'Neon Overpass',2023,'A concept album about a city built entirely from streetlights.'),
  (4,3,'Closet Symphony',2025,'The debut. Written, performed, and mixed in one bedroom.'),
  (5,4,'Last Bus Manifesto',2022,'Recorded in a single overnight session.'),
  (6,5,'Tideglass',2024,'A slow, reverb-drenched record about leaving a coastal town.'),
  (7,6,'Static Hours',2021,'Six long-form pieces meant to be played on loop.'),
  (8,7,'Feedback Weather',2023,'Guitars recorded through three amps stacked in a stairwell.'),
  (9,8,'Rhodes & Rain',2025,'A rainy-Sunday record built around one Rhodes piano.'),
  (10,9,'Patch Notes',2026,'Liner notes are just changelogs nobody asked for.'),
  (11,10,'Paper Cuts',2023,'Recorded in a garage, mixed in a bedroom.'),
  (12,11,'Condensation',2025,'A record about weather that doesn''t exist yet.'),
  (13,12,'Slow Town',2022,'Ten songs about places you''ve already forgotten.'),
  (14,13,'Static Bloom',2024,'The synth-pop record the algorithm didn''t see coming.');

INSERT OR IGNORE INTO tracks VALUES
  (1,1,'Anchor Weather',214),(2,1,'Porchlight',198),(3,1,'Low Tide Letters',241),(34,1,'Harbor Noise',176),
  (4,2,'Thunder on the Porch',188),(5,2,'Static and Rain',203),
  (6,3,'Neon Overpass',256),(7,3,'Vector Drive',231),(8,3,'Analog Skyline',219),(35,3,'Midnight Frequency',224),
  (9,4,'Closet Symphony',179),(10,4,'Laptop Fan Lullaby',162),(11,4,'Bedroom Pop Star',195),(36,4,'Tape Hiss Interlude',97),
  (12,5,'Last Bus',201),(13,5,'Manifesto',177),
  (14,6,'Tideglass',264),(15,6,'Leaving the Coast',233),(37,6,'Undertow',211),
  (16,7,'Static Hours I',312),(17,7,'Static Hours II',298),
  (18,8,'Feedback Weather',227),(19,8,'Stairwell Amp',214),
  (20,9,'Rhodes & Rain',241),(21,9,'Sunday Groove',208),(38,9,'Rain Interlude',88),
  (22,10,'Zero Day Lullaby',133),
  (23,11,'Paper Cuts',187),(24,11,'Garage Door',201),(25,11,'Vinyl Argument',165),
  (26,12,'Condensation',234),(27,12,'Patch Bay',198),
  (28,13,'Slow Town',221),(29,13,'Forgotten Places',204),(30,13,'Porch Light',179),
  (31,14,'Static Bloom',192),(32,14,'Broken TV',176),(33,14,'Bright Hooks',188);

INSERT OR IGNORE INTO playlists VALUES
  (1,1,'Late Night Drives','Synthwave and dream pop for the highway after midnight.',0),
  (2,1,'Rainy Day Focus','Ambient and lo-fi for getting things done.',0),
  (3,2,'Bedroom Pop Essentials','Everything Marigold Static and friends.',0),
  (4,1,'Founders'' Demo Vault','Unreleased demos and early mixes. Internal only. FLAG{wf_private_playlist_idor}',1),
  (5,1,'Q3 A&R Shortlist','Artists under consideration for the front page. Not for public eyes yet.',1),
  (6,5,'Shoegaze & Feedback','Walls of guitar, buried vocals, volume that only goes one way.',0),
  (7,6,'Sunday Focus, Vol. 2','More ambient and lo-fi for the second cup of coffee.',0),
  (8,7,'Post-Punk Revival','Angular guitars, sharper opinions.',0),
  (9,4,'Neo-Soul Sunday Mornings','Rhodes piano, unhurried grooves, slow mornings.',0),
  (10,2,'The CommonHuman Mixtape','A community-made mix. Proceeds fund more OctoRig labs.',0),
  (11,2,'Guilty Pleasures','Don''t judge me. (This is entirely fictional, please.)',1),
  (12,3,'Demo Voice Memos','Half-finished ideas, mostly humming into a laptop mic.',1),
  (13,4,'Study Grind','No lyrics allowed past 9pm. Purely made-up rule.',1),
  (14,5,'Pregame Mix','Volume goes to eleven before the show. Fictional show.',1),
  (15,6,'3am Ambient Dump','Field recordings I''m too embarrassed to publish yet.',1),
  (16,7,'Breakup Playlist (Do Not Share)','It''s not about anyone in particular. Fake breakup, real playlist.',1);

INSERT OR IGNORE INTO playlist_tracks VALUES
  (1,1,6),(2,1,7),(3,1,14),(4,1,15),
  (5,2,7),(6,2,16),(7,2,17),(8,2,20),
  (9,3,9),(10,3,10),(11,3,11),
  (12,4,2),(13,4,12),
  (14,5,18),(15,5,21),
  (16,6,18),(17,6,19),(18,6,16),
  (19,7,14),(20,7,15),(21,7,17),
  (22,8,12),(23,8,13),
  (24,9,20),(25,9,21),
  (26,10,22),(27,10,6),(28,10,9),
  (29,11,3),(30,12,9),(31,13,20),(32,14,6),(33,15,14),(34,16,4);

INSERT OR IGNORE INTO royalties VALUES
  (1,1,'2026-Q1',18420.50,'Standard streaming payout, on schedule.'),
  (2,2,'2026-Q1',9410.75,'Payout pending — banking details under review. FLAG{wf_royalties_idor}'),
  (3,3,'2026-Q1',6120.00,'Standard streaming payout, on schedule.'),
  (4,4,'2026-Q1',4210.25,'Standard streaming payout, on schedule.');

INSERT OR IGNORE INTO _flags VALUES
  (1,'sqli-union','FLAG{wf_union_select_from_flags}');

INSERT OR IGNORE INTO plays VALUES
  (1,1,22,'2026-08-15T02:14:00Z','Private A&R preview, not for public ears yet. FLAG{wf_recent_plays_idor}'),
  (2,2,9,'2026-08-20T14:02:00Z','Replayed for the fourth time this week.'),
  (3,3,16,'2026-08-21T09:40:00Z','Volume: too loud, as always.'),
  (4,4,20,'2026-08-22T22:15:00Z','Sunday morning coffee soundtrack.'),
  (5,5,18,'2026-08-23T19:30:00Z','Still not tired of this one.'),
  (6,6,14,'2026-08-24T23:05:00Z','On loop since the release.'),
  (7,7,4,'2026-08-25T08:12:00Z','Commute music, obviously.'),
  (8,1,2,'2026-08-19T10:00:00Z','Morning playlist filler.'),
  (9,1,11,'2026-08-26T20:45:00Z','Testing the new EQ curve.');

INSERT OR IGNORE INTO follows VALUES
  (1,1,9,'Keeping an eye on this one before anyone else notices. FLAG{wf_follows_idor}'),
  (2,2,3,'Been following since the debut EP.'),
  (3,3,8,'That Rhodes tone is unbeatable.'),
  (4,4,5,'Dream pop supremacy.'),
  (5,5,7,'Wall of sound, forever.'),
  (6,6,6,'Perfect for late-night mixing sessions.'),
  (7,7,4,'Saw them live once. Never recovered.'),
  (8,1,3,'Keeping tabs on the competition.'),
  (9,1,2,'Good synths, better merch.');
"""


def get_db():
    db = getattr(g, '_db', None)
    if db is None:
        db = g._db = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


def close_db(_):
    db = getattr(g, '_db', None)
    if db:
        db.close()


def init_db():
    os.makedirs('/data', exist_ok=True)
    conn = sqlite3.connect(DATABASE)
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()
    with open('/flag_insane.txt', 'w') as f:
        f.write('FLAG{wf_insane_ssrf_cmdi_chain}\n')
