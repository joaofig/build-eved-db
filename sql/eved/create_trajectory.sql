CREATE TABLE trajectory (
    traj_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicle_id  INTEGER NOT NULL,
    trip_id     INTEGER NOT NULL,
    length_m    DOUBLE,
    dt_ini      TEXT,
    dt_end      TEXT,
    duration_s  DOUBLE
);
