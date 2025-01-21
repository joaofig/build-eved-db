INSERT INTO trajectory (vehicle_id, trip_id)
    SELECT DISTINCT vehicle_id, trip_id FROM signal;
