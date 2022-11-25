DROP TABLE IF EXISTS tds;
DROP TABLE IF EXISTS hydration;

CREATE TABLE tds (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  tds INTEGER NOT NULL
);

CREATE TABLE hydration (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  created TIMESTAMP NOT NULL DEFAULT (datetime('now','localtime')),
  differ INTEGER NOT NULL,
  current_vol INTEGER NOT NULL
);

INSERT INTO hydration (differ, current_vol)
    VALUES (0, 0);