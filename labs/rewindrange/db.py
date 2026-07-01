import os
import sqlite3
from flask import g

DATABASE = '/data/rewind.db'

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id         INTEGER PRIMARY KEY,
    username   TEXT UNIQUE NOT NULL,
    password   TEXT NOT NULL,
    email      TEXT NOT NULL,
    first_name TEXT DEFAULT '',
    last_name  TEXT DEFAULT '',
    is_admin   INTEGER DEFAULT 0,
    address    TEXT DEFAULT '',
    phone      TEXT DEFAULT '',
    balance    REAL DEFAULT 100.00
);

CREATE TABLE IF NOT EXISTS products (
    id          INTEGER PRIMARY KEY,
    type        TEXT NOT NULL,
    title       TEXT NOT NULL,
    creator     TEXT NOT NULL,
    genre       TEXT NOT NULL,
    year        INTEGER NOT NULL,
    price       REAL NOT NULL,
    stock       INTEGER DEFAULT 5,
    description TEXT DEFAULT '',
    condition   TEXT DEFAULT 'Good',
    platform    TEXT DEFAULT NULL
);

CREATE TABLE IF NOT EXISTS orders (
    id               INTEGER PRIMARY KEY,
    user_id          INTEGER NOT NULL,
    order_date       TEXT NOT NULL,
    status           TEXT DEFAULT 'pending',
    total            REAL NOT NULL,
    shipping_address TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS order_items (
    id         INTEGER PRIMARY KEY,
    order_id   INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    price      REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS wishlists (
    id         INTEGER PRIMARY KEY,
    user_id    INTEGER NOT NULL,
    product_id INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS reviews (
    id          INTEGER PRIMARY KEY,
    product_id  INTEGER NOT NULL,
    user_id     INTEGER NOT NULL,
    rating      INTEGER NOT NULL,
    text        TEXT NOT NULL,
    review_date TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS feedback (
    id           INTEGER PRIMARY KEY,
    name         TEXT NOT NULL,
    email        TEXT NOT NULL,
    message      TEXT NOT NULL,
    submitted_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS coupons (
    id           INTEGER PRIMARY KEY,
    code         TEXT NOT NULL,
    discount_pct INTEGER NOT NULL,
    description  TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS board_threads (
    id        INTEGER PRIMARY KEY,
    user_id   INTEGER NOT NULL,
    title     TEXT NOT NULL,
    body      TEXT NOT NULL,
    posted_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS board_replies (
    id        INTEGER PRIMARY KEY,
    thread_id INTEGER NOT NULL,
    user_id   INTEGER NOT NULL,
    body      TEXT NOT NULL,
    posted_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS messages (
    id      INTEGER PRIMARY KEY,
    from_id INTEGER NOT NULL,
    to_id   INTEGER NOT NULL,
    subject TEXT NOT NULL,
    body    TEXT NOT NULL,
    sent_at TEXT NOT NULL,
    read    INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS _flags (
    id    INTEGER PRIMARY KEY,
    name  TEXT UNIQUE NOT NULL,
    value TEXT NOT NULL
);

INSERT OR IGNORE INTO users VALUES
  (1,'admin','123456789','admin@rewind.local','Admin','User',1,'1 Static Lane, Hollywood CA','555-0100',250.00),
  (2,'alice','iloveyou','alice@example.com','Alice','Hendricks',0,'42 Oak Street, Portland OR','555-0101',100.00),
  (3,'bob','superman','bob@example.com','Bob','Slater',0,'7 Elm Ave, Seattle WA','555-0102',100.00),
  (4,'carol','princess','carol@example.com','Carol','Kane',0,'99 Pine Road, Austin TX','555-0103',100.00),
  (5,'jess','loveyou','jess@example.com','Jessica','Palmer',0,'18 Maple Drive, Denver CO','555-0104',100.00),
  (6,'marcus','basketball','marcus@example.com','Marcus','Webb',0,'5 Cedar Close, Nashville TN','555-0105',100.00),
  (7,'tanya','starwars','tanya@example.com','Tanya','Mills',0,'301 Birch Road, Chicago IL','555-0106',100.00),
  (8,'dave','rockyou','dave@example.com','Dave','Cross',0,'77 Willow Lane, Miami FL','555-0107',100.00);

INSERT OR IGNORE INTO coupons VALUES
  (1,'REWIND10',10,'10% off your order'),
  (2,'VHS20',20,'20% off for VHS fans'),
  (3,'GAMEON15',15,'15% off retro games'),
  (4,'MEMBER5',5,'5% member loyalty discount');

INSERT OR IGNORE INTO products VALUES
  (1,'vhs','The Terminator','James Cameron','Action / Sci-Fi',1984,9.99,8,
   'A cyborg assassin is sent back in time to kill Sarah Connor before she can change the future.','VG+',NULL),
  (2,'vhs','Ghostbusters','Ivan Reitman','Comedy / Horror',1984,7.99,6,
   'Three parapsychology professors start a ghost-catching business in New York City.','Good',NULL),
  (3,'vhs','Blade Runner','Ridley Scott','Sci-Fi / Noir',1982,12.99,3,
   'A cynical cop hunts rogue replicants in a rain-soaked dystopian Los Angeles.','Excellent',NULL),
  (4,'vhs','Back to the Future','Robert Zemeckis','Sci-Fi / Comedy',1985,8.99,9,
   'A teenager is accidentally sent 30 years into the past in a DeLorean time machine.','Good',NULL),
  (5,'vhs','Aliens','James Cameron','Action / Sci-Fi',1986,9.99,5,
   'Ripley returns to the alien planet with a unit of marines to face a colony of xenomorphs.','VG',NULL),
  (6,'vhs','The Thing','John Carpenter','Horror / Sci-Fi',1982,11.99,4,
   'A shape-shifting alien organism terrorises a group of researchers in Antarctica.','Good',NULL),
  (7,'vhs','Predator','John McTiernan','Action / Sci-Fi',1987,8.99,7,
   'An elite military rescue team is hunted by an extraterrestrial warrior in a Central American jungle.','VG',NULL),
  (8,'vhs','RoboCop','Paul Verhoeven','Action / Sci-Fi',1987,9.99,5,
   'A murdered Detroit cop is rebuilt as a cyborg law enforcer and uncovers corporate corruption.','Good',NULL),
  (9,'vhs','Die Hard','John McTiernan','Action / Thriller',1988,7.99,10,
   'A New York City cop battles terrorists who have taken over a Los Angeles skyscraper.','Good',NULL),
  (10,'vhs','Total Recall','Paul Verhoeven','Action / Sci-Fi',1990,8.99,6,
   'A construction worker discovers his memories of Mars may be part of a spy fantasy turned real.','VG',NULL),
  (11,'vhs','WarGames','John Badham','Thriller / Drama',1983,9.99,4,
   'A young hacker accidentally accesses a military supercomputer and nearly starts World War III.','VG+',NULL),
  (12,'vhs','Tron','Steven Lisberger','Sci-Fi / Adventure',1982,11.99,2,
   'A computer programmer is digitised and transported into a world of gladiatorial games.','Excellent',NULL),
  (13,'game','Super Mario Bros.','Nintendo','Platformer',1985,14.99,5,
   'Run, jump and stomp your way through the Mushroom Kingdom to rescue Princess Peach.','Good','NES'),
  (14,'game','The Legend of Zelda','Nintendo','Action / Adventure',1986,19.99,3,
   'Guide Link across Hyrule, solve dungeons and recover the Triforce of Wisdom.','VG+','NES'),
  (15,'game','Mega Man 2','Capcom','Platformer / Action',1988,13.99,4,
   'Choose your stage order and battle eight robot masters to stop the evil Dr. Wily.','Good','NES'),
  (16,'game','Sonic the Hedgehog','Sega','Platformer',1991,12.99,6,
   'Blast through Green Hill Zone and beyond at supersonic speed to defeat Dr. Robotnik.','VG','Genesis'),
  (17,'game','Mortal Kombat','Midway','Fighting',1993,14.99,5,
   'Tournament-grade one-on-one fighting with digitised fighters and brutal finishing moves.','Good','Genesis'),
  (18,'game','Street Fighter II','Capcom','Fighting',1992,16.99,4,
   'Choose from twelve world warriors and battle your way to face M. Bison.','VG+','SNES'),
  (19,'game','Donkey Kong Country','Rare','Platformer',1994,18.99,3,
   'Pre-rendered 3D graphics and relentless platform action across Donkey Kong Island.','Excellent','SNES'),
  (20,'game','Super Metroid','Nintendo','Action / Adventure',1994,22.99,2,
   'Track Samus through the cavernous planet Zebes in one of the greatest games ever made.','VG+','SNES'),
  (21,'game','GoldenEye 007','Rare','First-Person Shooter',1997,24.99,4,
   'The definitive N64 shooter — single-player missions and legendary four-player split-screen.','Good','N64'),
  (22,'game','The Legend of Zelda: Ocarina of Time','Nintendo','Action / Adventure',1998,29.99,2,
   'Link''s first 3D adventure — the water temple awaits.','Excellent','N64'),
  (23,'game','Pac-Man','Atari','Arcade',1982,6.99,7,
   'The classic maze chase game — eat dots, avoid ghosts, chase the high score.','Fair','Atari 2600'),
  (24,'game','Pitfall!','Activision','Platformer / Adventure',1982,8.99,5,
   'Swing on vines, leap over scorpions and crocodiles across 255 jungle screens.','Good','Atari 2600'),
  (25,'game','Doom','id Software','First-Person Shooter',1993,9.99,4,
   'The grandfather of the FPS genre. Rip and tear through demon-infested Mars base UAC.','Good','PC'),
  (26,'game','CommonHuman-Lab','CommonHuman','Experimental',2026,999.99,1,
   'A mysterious product that defies categorisation. Handle with care.','Mint','PC'),
  (27,'vhs','The CommonHuman Experiment','CommonHuman','Experimental / Documentary',2026,149.99,1,
   'An unclassified production. What you are about to see cannot be unseen.','Mint',NULL);

INSERT OR IGNORE INTO orders VALUES
  (1,2,'2026-04-28','delivered',22.98,'42 Oak Street, Portland OR'),
  (2,2,'2026-05-10','shipped',19.99,'42 Oak Street, Portland OR'),
  (3,3,'2026-05-05','pending',37.97,'7 Elm Ave, Seattle WA'),
  (4,4,'2026-05-15','processing',22.99,'99 Pine Road, Austin TX'),
  (5,1,'2026-05-18','delivered',47.98,'1 Static Lane, Hollywood CA · FLAG{rw_api_idor_rentals}'),
  (6,5,'2026-04-30','delivered',32.98,'18 Maple Drive, Denver CO'),
  (7,6,'2026-05-02','delivered',35.97,'5 Cedar Close, Nashville TN'),
  (8,7,'2026-05-06','shipped',34.98,'301 Birch Road, Chicago IL'),
  (9,8,'2026-05-08','delivered',32.98,'77 Willow Lane, Miami FL'),
  (10,2,'2026-05-12','delivered',33.98,'42 Oak Street, Portland OR'),
  (11,3,'2026-05-14','shipped',38.98,'7 Elm Ave, Seattle WA'),
  (12,4,'2026-05-16','processing',21.98,'99 Pine Road, Austin TX'),
  (13,5,'2026-05-17','pending',23.98,'18 Maple Drive, Denver CO'),
  (14,6,'2026-05-18','processing',30.98,'5 Cedar Close, Nashville TN'),
  (15,7,'2026-05-19','pending',25.97,'301 Birch Road, Chicago IL'),
  (16,8,'2026-05-20','shipped',19.98,'77 Willow Lane, Miami FL'),
  (17,2,'2026-05-21','pending',23.98,'42 Oak Street, Portland OR');

INSERT OR IGNORE INTO order_items VALUES
  (1,1,1,9.99),(2,1,13,14.99),
  (3,2,14,19.99),
  (4,3,9,7.99),(5,3,18,16.99),(6,3,16,12.99),
  (7,4,20,22.99),
  (8,5,3,12.99),(9,5,21,24.99),(10,5,6,11.99),
  (11,6,3,12.99),(12,6,14,19.99),
  (13,7,2,7.99),(14,7,16,12.99),(15,7,13,14.99),
  (16,8,6,11.99),(17,8,20,22.99),
  (18,9,9,7.99),(19,9,21,24.99),
  (20,10,13,14.99),(21,10,19,18.99),
  (22,11,22,29.99),(23,11,10,8.99),
  (24,12,12,11.99),(25,12,11,9.99),
  (26,13,7,8.99),(27,13,17,14.99),
  (28,14,18,16.99),(29,14,15,13.99),
  (30,15,4,8.99),(31,15,23,6.99),(32,15,25,9.99),
  (33,16,5,9.99),(34,16,8,9.99),
  (35,17,11,9.99),(36,17,15,13.99);

INSERT OR IGNORE INTO wishlists VALUES
  (1,2,3),(2,2,6),(3,2,22),
  (4,3,1),(5,3,19),(6,3,25),
  (7,4,21),(8,4,12),
  (9,5,1),(10,5,8),(11,5,21),
  (12,6,3),(13,6,20),(14,6,22),
  (15,7,12),(16,7,19),(17,7,21),
  (18,8,3),(19,8,14),(20,8,22),
  (21,2,26),(22,3,27),(23,5,26),(24,8,27);

INSERT OR IGNORE INTO reviews VALUES
  (1,1,2,5,'Absolute classic. The practical effects still hold up after all these years.','2026-04-29'),
  (2,3,3,5,'Blade Runner is pure cinema. Worth every penny for any collector.','2026-05-06'),
  (3,13,4,5,'Perfect condition cartridge. Blows into it once and it works every time.','2026-05-11'),
  (4,21,2,5,'The split-screen sessions with my flatmates were legendary. Great find.','2026-05-12'),
  (5,14,3,4,'Cartridge works perfectly. The fold-out map is included too, which is a bonus.','2026-05-14'),
  (6,1,3,4,'Great action flick. Print quality is surprisingly sharp for the era.','2026-04-30'),
  (7,1,5,5,'Still gives me chills every single watch. Quintessential 80s sci-fi.','2026-05-02'),
  (8,2,2,5,'One of the greatest comedies ever put on tape. Buy it immediately.','2026-05-03'),
  (9,2,4,4,'Slimer gets me every time. Tape is in great shape.','2026-05-20'),
  (10,3,4,5,'The atmosphere is completely unmatched. A genuine film artefact.','2026-05-07'),
  (11,3,7,5,'Watched this three times in a week. The replicant scenes are haunting.','2026-05-08'),
  (12,4,4,5,'Family favourite. The DeLorean sequences hold up brilliantly.','2026-05-09'),
  (13,4,5,4,'Bought this as a gift for my dad. Perfect tape quality.','2026-05-16'),
  (14,5,5,5,'Vasquez. That is all. Essential purchase.','2026-05-13'),
  (15,6,5,5,'The transformation scenes are terrifying even now. Essential horror.','2026-05-19'),
  (16,7,3,5,'Get to the choppa! Perfect tape copy too.','2026-05-04'),
  (17,8,8,5,'Dead or alive, you are coming with me. Still absolutely brilliant.','2026-05-20'),
  (18,9,8,5,'Yippee-ki-yay. A masterpiece. Tape is in excellent shape.','2026-05-11'),
  (19,10,7,4,'Total Recall aged way better than expected. The Mars sets are wild.','2026-05-17'),
  (20,11,5,5,'WarGames is more relevant now than in 1983. Excellent condition.','2026-05-18'),
  (21,13,2,5,'Mario is genuinely timeless. Cartridge blew right to life first try.','2026-05-11'),
  (22,13,3,5,'Best game ever made, full stop. My thumbs are still sore.','2026-05-15'),
  (23,14,5,5,'The golden cartridge still delivers after all these years.','2026-05-14'),
  (24,14,2,5,'Got the fold-out map with mine as well. Absolutely legendary.','2026-05-16'),
  (25,15,5,5,'Mega Man 2 is the pinnacle of NES game design. Immaculate condition.','2026-05-17'),
  (26,18,6,5,'Street Fighter II is still the benchmark for fighting games. Perfect port.','2026-05-18'),
  (27,19,7,4,'Donkey Kong Country still looks incredible. What a SNES showcase.','2026-05-19'),
  (28,20,7,5,'Super Metroid is a masterpiece. Best copy I have ever owned.','2026-05-20'),
  (29,21,3,5,'Four-player mode destroyed friendships in the best way possible.','2026-05-12'),
  (30,21,8,5,'The campaign still holds up. Facility bathroom. Enough said.','2026-05-13'),
  (31,22,5,5,'Ocarina of Time is the greatest game ever made. Perfect cart.','2026-05-14'),
  (32,22,6,5,'Nothing has come close in 25 years. The Kokiri Forest music still hits.','2026-05-15'),
  (33,25,8,4,'The IDDQD codes work fine. Brilliant rip-and-tear purchase.','2026-05-21'),
  (34,26,1,5,'There are no words. Whatever this is — it runs. Handle with care indeed.','2026-05-20'),
  (35,26,4,5,'I have never seen anything like it. The executable defies description. Five stars is not enough.','2026-05-21'),
  (36,26,7,5,'Experimental does not even begin to cover it. Mint condition. It will change how you think about software.','2026-05-22'),
  (37,27,1,5,'Do not watch this alone. The print quality is flawless and the content is... something else entirely.','2026-05-20'),
  (38,27,3,5,'I do not know what I watched but I cannot stop thinking about it. Mint condition. Worth every penny.','2026-05-21'),
  (39,27,6,5,'Classified for a reason. The tape quality is immaculate. This one stays in the vault.','2026-05-22');

INSERT OR IGNORE INTO board_threads VALUES
  (1,2,'Best retro game to start collecting?','Just joined the store and looking for advice on where to start. I have a SNES and an NES. Any recommendations for must-haves?','2026-05-01'),
  (2,3,'VHS tape storage tips','Got a bunch of tapes from here and wondering about the best long-term storage. Upright or flat? Does temperature matter?','2026-05-03'),
  (3,4,'Just received Ocarina of Time — blown away','Ordered the N64 cartridge last week and it arrived in perfect condition today. The label is immaculate. Worth every penny.','2026-05-15'),
  (4,6,'How do you spot a fake cartridge?','Picked up what I thought was a legit copy of Mario 64 at a car boot. The label feels slightly off. Any tips on spotting fakes before buying?','2026-05-08'),
  (5,7,'Delivery times lately?','Has anyone had delays recently? My order from two weeks ago is still showing as shipped with no movement.','2026-05-19'),
  (6,5,'Street Fighter II or Mortal Kombat?','Classic debate. I grew up on MK but the SFII port on SNES is technically superior in almost every way. Thoughts?','2026-05-10'),
  (7,8,'Finally found a clean copy of WarGames','Been hunting for months. Just picked it up here and could not be happier with the condition. The case is near mint.','2026-05-18');

INSERT OR IGNORE INTO board_replies VALUES
  (1,1,3,'Start with Super Mario Bros or Zelda on NES. Both are cheap and define the era perfectly.','2026-05-02'),
  (2,1,6,'Donkey Kong Country if you have a SNES. The pre-rendered graphics and soundtrack are still incredible.','2026-05-02'),
  (3,1,5,'GoldenEye for N64 if you can stretch that far. The four-player mode alone justifies the price.','2026-05-03'),
  (4,2,4,'Always store VHS upright, like books on a shelf. Never lay them flat. Keep away from magnets and sunlight.','2026-05-04'),
  (5,2,7,'A cool dry place is the main thing. Mine have been in a wardrobe for 30 years and play perfectly.','2026-05-05'),
  (6,3,2,'Jealous! That is one of the cleanest carts in their stock. Enjoy every second of it.','2026-05-15'),
  (7,3,8,'The Kokiri Forest music hit me all over again last time I booted it up. Absolute masterpiece.','2026-05-16'),
  (8,4,3,'Check the screw type on the back. Official Nintendo carts use security screws. Fakes usually use standard Phillips.','2026-05-09'),
  (9,4,2,'The PCB colour under UV light can tell you a lot too. Most fakes use the wrong shade of green.','2026-05-10'),
  (10,6,3,'Street Fighter II all day. The SNES port was as close to arcade perfect as you could get at home in 1992.','2026-05-11'),
  (11,6,4,'MK had the blood code on Genesis and SFII did not. That was a huge deal at the time.','2026-05-12'),
  (12,5,1,'Apologies for the delay — there have been carrier issues in some regions this week. Should resolve by Friday.','2026-05-20');

INSERT OR IGNORE INTO messages VALUES
  (1,1,2,'Welcome to Rewind Range','Hi Alice, thanks for joining. Let us know if you have any questions about your orders or anything in the collection. FLAG{rw_idor_inbox_read}','2026-04-29',1),
  (2,2,3,'Seen the new arrivals?','Bob, did you check the new SNES stock that came in this week? Some real gems in there.','2026-05-11',1),
  (3,3,4,'Your review helped me decide','Carol, I bought Blade Runner after reading your review. You were absolutely right — the print quality is exceptional.','2026-05-08',1),
  (4,4,2,'Delivery question','Alice, did your last order arrive okay? Mine is showing as delivered but nothing has turned up.','2026-05-17',0),
  (5,6,5,'SFII vs MK','Jess, saw your board post. Street Fighter II is objectively better but I will never stop loving MK either.','2026-05-11',1),
  (6,7,8,'WarGames copy','Dave, the copy I got from here is in excellent shape. Worth grabbing if they restock.','2026-05-19',0),
  (7,1,3,'Order #11 update','Hi Bob, your order has been dispatched and should arrive within two to three working days.','2026-05-15',1),
  (8,8,6,'GoldenEye session','Marcus, we need to arrange a four-player GoldenEye night. I have the TV, the N64, and four controllers.','2026-05-21',0);

INSERT OR IGNORE INTO _flags VALUES
  (1,'sqli-union',       'FLAG{rw_union_select_from_flags}'),
  (3,'python-sqli',      'FLAG{rw_python_sqli_automated}');
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
    for migration in [
        "ALTER TABLE users ADD COLUMN balance REAL DEFAULT 100.00",
        "ALTER TABLE users ADD COLUMN bio TEXT DEFAULT ''",
    ]:
        try:
            conn.execute(migration)
        except sqlite3.OperationalError:
            pass
    conn.executescript("""
        UPDATE users SET bio = 'Retro collector since the 90s. VHS is life. Hunting rare tapes one at a time.' WHERE id = 2 AND bio = '';
        UPDATE users SET bio = 'SNES purist. If it does not have Mode 7, I am not interested.' WHERE id = 3 AND bio = '';
        UPDATE users SET bio = 'Chasing every good VHS tape I can find. The rarer the better.' WHERE id = 4 AND bio = '';
        UPDATE users SET bio = 'Fighting game fanatic. Street Fighter II changed everything for me in 1992.' WHERE id = 6 AND bio = '';
        UPDATE users SET bio = 'N64 loyalist. Four-player GoldenEye nights are what weekends are for.' WHERE id = 7 AND bio = '';
        UPDATE users SET bio = 'Doom and Quake. Everything else is a tech demo.' WHERE id = 8 AND bio = '';
    """)
    conn.commit()
    conn.close()
