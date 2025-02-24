CREATE TABLE IF NOT EXISTS node
(
    node_id         INTEGER PRIMARY KEY ASC,
    traj_id         INTEGER NOT NULL,
    latitude        DOUBLE,
    longitude       DOUBLE,
    h3_12           INTEGER,
    match_error     TEXT
);