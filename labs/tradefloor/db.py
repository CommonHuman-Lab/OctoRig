import os
import sqlite3
from flask import g

DATABASE = '/data/tradefloor.db'

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id        INTEGER PRIMARY KEY,
    username  TEXT UNIQUE NOT NULL,
    password  TEXT NOT NULL,
    email     TEXT NOT NULL,
    full_name TEXT DEFAULT '',
    is_admin  INTEGER DEFAULT 0,
    bio       TEXT DEFAULT '',
    phone     TEXT DEFAULT '',
    address   TEXT DEFAULT '',
    balance   REAL DEFAULT 10000.0
);

CREATE TABLE IF NOT EXISTS portfolio_holdings (
    id        INTEGER PRIMARY KEY,
    user_id   INTEGER NOT NULL,
    symbol    TEXT NOT NULL,
    quantity  INTEGER DEFAULT 0,
    avg_price REAL DEFAULT 0.0
);

CREATE TABLE IF NOT EXISTS orders (
    id           INTEGER PRIMARY KEY,
    user_id      INTEGER NOT NULL,
    symbol       TEXT NOT NULL,
    action       TEXT NOT NULL,
    quantity     INTEGER NOT NULL,
    order_type   TEXT NOT NULL,
    price        REAL DEFAULT 0.0,
    status       TEXT DEFAULT 'open',
    created_at   TEXT NOT NULL,
    memo         TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS market_data (
    id     INTEGER PRIMARY KEY,
    symbol TEXT UNIQUE NOT NULL,
    name   TEXT NOT NULL,
    price  REAL NOT NULL,
    change REAL DEFAULT 0.0,
    sector TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS watchlist (
    id      INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    symbol  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS filings (
    id         INTEGER PRIMARY KEY,
    symbol     TEXT NOT NULL,
    title      TEXT NOT NULL,
    body       TEXT NOT NULL,
    sector     TEXT DEFAULT '',
    filed_date TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS alerts (
    id         INTEGER PRIMARY KEY,
    user_id    INTEGER NOT NULL,
    name       TEXT NOT NULL,
    symbol     TEXT NOT NULL,
    condition  TEXT NOT NULL,
    threshold  REAL NOT NULL,
    active     INTEGER DEFAULT 1,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS reset_tokens (
    id         INTEGER PRIMARY KEY,
    user_id    INTEGER NOT NULL,
    token      TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    used       INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS price_history (
    id          INTEGER PRIMARY KEY,
    symbol      TEXT NOT NULL,
    price       REAL NOT NULL,
    recorded_at TEXT NOT NULL,
    UNIQUE(symbol, recorded_at)
);

INSERT OR IGNORE INTO users VALUES
  (1,'admin','commonhuman-lab','admin@tradefloor.local','TradeFloor Admin',1,'','','',50000.0),
  (2,'alice.p','abc1234','alice@example.com','Alice Porter',0,'Day trader since 1996.','','12 Wall St, New York NY',48320.50),
  (3,'bob.nash','pass1234','bob@example.com','Bob Nash',0,'','','34 Market St, San Francisco CA',12750.00),
  (4,'carol.wu','tiger99','carol@example.com','Carol Wu',0,'Tech sector focused.','','88 Pine Ave, Seattle WA',31200.00),
  (5,'dan.ford','monkey1','dan@example.com','Dan Ford',0,'','','55 Oak Blvd, Austin TX',6800.00),
  (6,'eva.lin','summer98','eva@example.com','Eva Lin',0,'Value investor.','','9 Birch Rd, Chicago IL',92100.00),
  (7,'frank.oz','letme1n','frank@example.com','Frank Oz',0,'','','77 Elm Ct, Denver CO',15500.00);

INSERT OR IGNORE INTO market_data VALUES
  (1, 'ACME','Acme Corporation',     42.50,  1.20,'Technology'),
  (2, 'NOVA','Nova Systems Inc',     18.75, -0.45,'Technology'),
  (3, 'BLKR','Blackrock Industries',  7.10,  0.05,'Energy'),
  (4, 'ZTRX','ZetaTronix Ltd',       93.00,  2.80,'Technology'),
  (5, 'PCFW','Pacific Forwarding',   14.20, -0.30,'Logistics'),
  (6, 'GMBT','Gambit Financial',     55.60,  0.90,'Finance'),
  (7, 'SLVR','Silverstream Media',   22.40, -1.10,'Media'),
  (8, 'CTRX','CentraTech Corp',      61.00,  0.00,'Technology'),
  (9, 'ARGX','Argos Exploration',     3.80,  0.15,'Energy'),
  (10,'HNTR','Hunter & Sons Ltd',    28.90, -0.60,'Retail'),
  (11,'CMNH','CommonHuman Labs',    1337.00, 5.00,'Experimental');

INSERT OR IGNORE INTO portfolio_holdings VALUES
  (1, 2,'ACME', 100, 38.20),
  (2, 2,'ZTRX',  20, 85.00),
  (3, 2,'GMBT',  50, 50.10),
  (4, 2,'SLVR',  75, 24.00),
  (5, 3,'NOVA', 200, 20.00),
  (6, 3,'BLKR', 500,  6.80),
  (7, 3,'PCFW', 100, 15.50),
  (8, 4,'ACME',  75, 40.00),
  (9, 4,'CTRX',  30, 58.00),
  (10,4,'ZTRX',  10, 80.00),
  (11,5,'ARGX',1000,  3.50),
  (12,5,'BLKR', 200,  7.00),
  (13,5,'HNTR',  50, 30.00),
  (14,6,'ZTRX',  80, 70.00),
  (15,6,'GMBT', 100, 48.00),
  (16,6,'ACME', 200, 35.00),
  (17,6,'CTRX',  60, 55.00),
  (18,7,'SLVR', 150, 25.00),
  (19,7,'NOVA', 100, 19.00),
  (20,7,'PCFW',  80, 14.00),
  (21,1,'ACME', 500, 30.00),
  (22,1,'ZTRX', 100, 60.00),
  (23,1,'GMBT', 200, 44.00);

INSERT OR IGNORE INTO orders VALUES
  (1, 2,'ACME','buy', 100,'market',38.20,'filled','1999-12-01',''),
  (2, 2,'ZTRX','buy',  20,'market',85.00,'filled','1999-12-05',''),
  (3, 2,'SLVR','buy',  75,'market',24.00,'filled','1999-12-10',''),
  (4, 2,'GMBT','buy',  50,'market',50.10,'filled','1999-12-15',''),
  (5, 2,'NOVA','sell', 50,'limit', 21.00,'open',  '2000-01-10',''),
  (6, 3,'NOVA','buy', 200,'market',20.00,'filled','1999-11-20',''),
  (7, 3,'BLKR','buy', 500,'market', 6.80,'filled','1999-11-22',''),
  (8, 3,'PCFW','buy', 100,'market',15.50,'filled','1999-12-01',''),
  (9, 3,'ACME','sell', 50,'limit', 44.00,'open',  '2000-01-12',''),
  (10,4,'ACME','buy',  75,'market',40.00,'filled','1999-10-15',''),
  (11,4,'CTRX','buy',  30,'market',58.00,'filled','1999-11-01',''),
  (12,4,'ZTRX','buy',  10,'market',80.00,'filled','1999-11-15',''),
  (13,4,'CTRX','buy',  20,'limit', 60.00,'open',  '2000-01-08',''),
  (14,5,'ARGX','buy',1000,'market', 3.50,'filled','1999-09-01',''),
  (15,5,'BLKR','buy', 200,'market', 7.00,'filled','1999-09-15',''),
  (16,5,'HNTR','buy',  50,'market',30.00,'filled','1999-10-01',''),
  (17,5,'ARGX','sell',500,'limit',  4.50,'open',  '2000-01-15',''),
  (18,6,'ZTRX','buy',  80,'market',70.00,'filled','1999-08-10',''),
  (19,6,'ACME','buy', 200,'market',35.00,'filled','1999-07-01',''),
  (20,6,'GMBT','buy', 100,'market',48.00,'filled','1999-08-20',''),
  (21,6,'CTRX','buy',  60,'market',55.00,'filled','1999-09-10',''),
  (22,7,'SLVR','buy', 150,'market',25.00,'filled','1999-10-20',''),
  (23,7,'NOVA','buy', 100,'market',19.00,'filled','1999-11-05',''),
  (24,7,'PCFW','buy',  80,'market',14.00,'filled','1999-11-18',''),
  (25,7,'SLVR','sell', 50,'limit', 24.00,'open',  '2000-01-20',''),
  (26,1,'ACME','buy', 500,'market',30.00,'filled','1999-06-01','FLAG{tf_idor_order_memo}'),
  (27,1,'ZTRX','buy', 100,'market',60.00,'filled','1999-07-15',''),
  (28,1,'GMBT','buy', 200,'market',44.00,'filled','1999-08-01',''),
  (29,1,'ZTRX','sell', 50,'limit',100.00,'open',  '2000-01-18','');

INSERT OR IGNORE INTO watchlist VALUES
  (1,2,'BLKR'),(2,2,'PCFW'),(3,2,'CTRX'),
  (4,3,'ACME'),(5,3,'ZTRX'),(6,3,'GMBT'),
  (7,4,'NOVA'),(8,4,'SLVR'),
  (9,5,'GMBT'),(10,5,'ZTRX'),(11,5,'CTRX'),
  (12,6,'NOVA'),(13,6,'PCFW'),
  (14,7,'ACME'),(15,7,'BLKR'),(16,7,'ZTRX'),
  (17,1,'CTRX'),(18,1,'HNTR'),(19,1,'SLVR'),(20,1,'CMNH');

INSERT OR IGNORE INTO filings VALUES
  (1,'ACME','Q4 1999 Earnings Report','Acme Corporation reported record Q4 earnings of $2.1 per share, beating analyst estimates by 12%. Revenue grew 34% year-over-year driven by strong demand for our enterprise software products. The board has authorised a $50M share buyback programme.','Technology','2000-01-15'),
  (2,'NOVA','Notice of Management Change','Nova Systems Inc announces the resignation of CEO James Holt and the appointment of Dr Sarah Bright as Acting Chief Executive with immediate effect. The board expressed full confidence in Dr Bright to lead the company through its strategic review.','Technology','2000-01-18'),
  (3,'BLKR','Acquisition of SolarDyne Assets','Blackrock Industries has completed the acquisition of SolarDyne asset portfolio for $14.8M. The assets include three operational wind generation sites and a 15-year power purchase agreement with Pacific Grid.','Energy','2000-01-20'),
  (4,'ZTRX','Prospectus Supplement — Secondary Offering','ZetaTronix Ltd is offering 2,000,000 shares of common stock at $90.00 per share. Proceeds will fund expansion into Asian markets and accelerate development of our next-generation processor architecture.','Technology','2000-01-22'),
  (5,'GMBT','Regulatory Filing — Form 10-K','Gambit Financial annual report for fiscal year 1999. Net income $88.4M, total assets $4.2B. Full report available upon request from the Investor Relations department.','Finance','2000-01-25'),
  (6,'ACME','Patent Grant — Distributed Processing Architecture','The US Patent and Trademark Office has granted Acme Corporation patent number 6,140,892 covering our proprietary distributed processing architecture. This patent strengthens our IP portfolio and provides competitive protection for our core product lines.','Technology','2000-01-28'),
  (7,'CMNH','Initial Public Offering — CommonHuman Labs','CommonHuman Labs is not a company. CommonHuman Labs is a question. We are filing this document in accordance with applicable regulations, but we offer no further guidance on what we do, what we make, or what we are. Sector: Experimental. Handle with care.','Experimental','2026-05-22');

CREATE TABLE IF NOT EXISTS _flags (
    id    INTEGER PRIMARY KEY,
    name  TEXT UNIQUE NOT NULL,
    value TEXT NOT NULL
);

INSERT OR IGNORE INTO _flags VALUES
  (1, 'sqli-market',   'FLAG{tf_union_select_from_flags}'),
  (2, 'sqli-api',      'FLAG{tf_api_token_injected}'),
  (3, 'sqli-creds',    'FLAG{tf_users_table_dumped}');

INSERT OR IGNORE INTO portfolio_holdings VALUES
  (24, 8,'CMNH', 10, 1300.00);

INSERT OR IGNORE INTO alerts VALUES
  (1, 2,'ACME above $45',    'ACME','above',45.00,1,'2000-01-05'),
  (2, 2,'ZTRX drop warning', 'ZTRX','below',90.00,1,'2000-01-06'),
  (3, 2,'GMBT target',       'GMBT','above',58.00,1,'2000-01-07'),
  (4, 3,'NOVA recovery',     'NOVA','above',22.00,1,'2000-01-08'),
  (5, 3,'BLKR cheap buy',    'BLKR','below', 6.50,1,'2000-01-09'),
  (6, 4,'CTRX target',       'CTRX','above',65.00,1,'2000-01-10'),
  (7, 4,'ZTRX pullback',     'ZTRX','below',88.00,1,'2000-01-11'),
  (8, 5,'ARGX exit',         'ARGX','above', 4.50,1,'2000-01-12'),
  (9, 5,'HNTR watch',        'HNTR','below',27.00,1,'2000-01-13'),
  (10,6,'GMBT momentum',     'GMBT','above',58.00,1,'2000-01-12'),
  (11,6,'ZTRX take profit',  'ZTRX','above',98.00,1,'2000-01-14'),
  (12,7,'SLVR rally',        'SLVR','above',24.00,1,'2000-01-15'),
  (13,7,'NOVA dip buy',      'NOVA','below',18.00,1,'2000-01-16'),
  (14,1,'ZTRX take profit',  'ZTRX','above',98.00,1,'2000-01-10'),
  (15,1,'ACME momentum',     'ACME','above',48.00,1,'2000-01-12');
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
    import random
    from datetime import datetime, timedelta, timezone
    os.makedirs('/data', exist_ok=True)
    conn = sqlite3.connect(DATABASE)
    conn.executescript(SCHEMA)
    try:
        conn.execute("ALTER TABLE orders ADD COLUMN memo TEXT DEFAULT ''")
    except sqlite3.OperationalError:
        pass
    try:
        conn.execute("ALTER TABLE portfolio_holdings ADD COLUMN notes TEXT DEFAULT ''")
    except sqlite3.OperationalError:
        pass
    conn.execute(
        "UPDATE portfolio_holdings SET notes = ? WHERE id = 24 AND (notes IS NULL OR notes = '')",
        ('FLAG{tf_python_idor_swept}',)
    )
    # Seed 60 price-history points (one per 10 s, going back 10 minutes) for each symbol
    stocks = conn.execute("SELECT symbol, price FROM market_data").fetchall()
    now = datetime.now(timezone.utc)
    for symbol, base_price in stocks:
        price = base_price
        for i in range(60, 0, -1):
            ts = (now - timedelta(seconds=i * 10)).strftime('%Y-%m-%dT%H:%M:%S')
            if symbol == 'CMNH':
                delta = round(price * random.uniform(-0.005, 0.005), 2)
            else:
                delta = round(price * random.uniform(-0.015, 0.015), 2)
            price = round(max(0.50, price + delta), 2)
            conn.execute(
                "INSERT OR IGNORE INTO price_history (symbol, price, recorded_at) VALUES (?, ?, ?)",
                (symbol, price, ts)
            )
    conn.commit()
    conn.close()
