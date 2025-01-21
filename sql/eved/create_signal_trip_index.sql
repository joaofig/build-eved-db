CREATE INDEX IF NOT EXISTS ix_signal_vehicle_trip ON signal (
    vehicle_id ASC,
    trip_id ASC,
    time_stamp ASC
);
