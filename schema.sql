CREATE TABLE IF NOT EXISTS leads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT,
    last_name TEXT,
    email TEXT NOT NULL,
    phone TEXT,
    company TEXT,
    source TEXT,
    message TEXT,
    status TEXT,
    score INTEGER,
    segment TEXT,
    converted INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lead_id INTEGER NOT NULL,
    event_type TEXT,
    details TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (lead_id) REFERENCES leads(id)
);

CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stripe_session_id TEXT UNIQUE,
    email TEXT NOT NULL,
    offer_name TEXT,
    target_client TEXT,
    problem TEXT,
    price TEXT,
    key_arguments TEXT,
    amount_paid INTEGER,
    currency TEXT DEFAULT 'eur',
    status TEXT DEFAULT 'pending',
    delivered INTEGER DEFAULT 0,
    delivery_error TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    paid_at DATETIME,
    delivered_at DATETIME
);
