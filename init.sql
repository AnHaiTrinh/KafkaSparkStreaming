\c app;
CREATE TABLE IF NOT EXISTS activity_logs (
  id SERIAL PRIMARY KEY,
  parking_lot_id INTEGER NOT NULL,
  license_plate VARCHAR(50) NOT NULL,
  vehicle_type VARCHAR(20) NOT NULL,
  activity_type VARCHAR(20) NOT NULL,
  created_at TIMESTAMP NOT NULL
);
INSERT INTO activity_logs (parking_lot_id, license_plate, vehicle_type, activity_type, created_at) VALUES
(1, '12345678', 'car', 'enter', '2021-10-01 10:00:03'),
(2, '02020101', 'car', 'exit', '2021-10-01 10:00:30'),
(3, '66666666', 'motorbike', 'enter', '2021-10-01 10:00:42'),
(4, '388923A9', 'car', 'enter', '2021-10-01 10:01:10'),
(5, '2939-B384', 'bicycle', 'exit', '2021-10-01 10:01:17'),
(6, '0002932I', 'car', 'exit', '2021-10-01 10:01:26');