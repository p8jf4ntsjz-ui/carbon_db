CREATE DATABASE IF NOT EXISTS carbon_db;
USE carbon_db;

CREATE TABLE IF NOT EXISTS emissions (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    category    VARCHAR(50)   NOT NULL,
    subcategory VARCHAR(100),
    amount      DECIMAL(10,2) NOT NULL,
    date        DATE          NOT NULL,
    notes       TEXT,
    created_at  TIMESTAMP     DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS monthly_targets (
    id        INT AUTO_INCREMENT PRIMARY KEY,
    year      INT NOT NULL,
    month     INT NOT NULL,
    target_kg DECIMAL(10,2) NOT NULL DEFAULT 900.00,
    UNIQUE KEY unique_month (year, month)
);

INSERT IGNORE INTO monthly_targets (year,month,target_kg) VALUES
(2026,1,1400),(2026,2,1300),(2026,3,1200),(2026,4,1100),(2026,5,1000),(2026,6,900);

INSERT INTO emissions (category,subcategory,amount,date,notes) VALUES
('transport','Car',120.50,'2026-01-10','Daily commute'),
('transport','Flight',850.00,'2026-01-15','Business trip Paris'),
('energy','Electricity',95.20,'2026-01-31','January bill'),
('energy','Natural Gas',60.80,'2026-01-31','Heating'),
('food','Beef',45.00,'2026-01-20','Weekly groceries'),
('food','Dairy',18.50,'2026-01-20','Weekly groceries'),
('waste','Landfill',12.30,'2026-01-31','Monthly waste'),
('shopping','Clothing',35.00,'2026-01-25','Winter jacket'),
('transport','Car',110.00,'2026-02-10','Daily commute'),
('energy','Electricity',88.40,'2026-02-28','February bill'),
('energy','Natural Gas',55.60,'2026-02-28','Heating'),
('food','Beef',42.00,'2026-02-15','Weekly groceries'),
('food','Vegetarian',8.00,'2026-02-22','Vegan week'),
('waste','Landfill',10.80,'2026-02-28','Monthly waste'),
('transport','Car',105.00,'2026-03-10','Daily commute'),
('transport','Public Transport',15.00,'2026-03-15','Metro'),
('energy','Electricity',72.00,'2026-03-31','March bill'),
('energy','Natural Gas',40.00,'2026-03-31','Less heating'),
('food','Beef',38.00,'2026-03-15','Weekly groceries'),
('food','Vegetarian',6.50,'2026-03-22','Vegan week'),
('waste','Recycling',5.00,'2026-03-31','Improved recycling'),
('shopping','Electronics',120.00,'2026-03-10','New keyboard'),
('transport','Car',100.00,'2026-04-10','Daily commute'),
('energy','Electricity',65.00,'2026-04-30','April bill'),
('food','Beef',30.00,'2026-04-15','Weekly groceries'),
('food','Vegetarian',7.00,'2026-04-22','Vegan week'),
('waste','Landfill',9.50,'2026-04-30','Monthly waste'),
('transport','Car',98.00,'2026-05-10','Daily commute'),
('transport','Cycling',0.00,'2026-05-15','Bike to work'),
('energy','Electricity',58.00,'2026-05-31','May bill'),
('food','Beef',25.00,'2026-05-15','Weekly groceries'),
('food','Vegetarian',9.00,'2026-05-22','More plant-based'),
('waste','Recycling',4.00,'2026-05-31','Recycling'),
('shopping','Clothing',28.00,'2026-05-20','Summer clothes'),
('transport','Car',95.00,'2026-06-05','Daily commute'),
('energy','Electricity',55.00,'2026-06-10','June so far'),
('food','Beef',22.00,'2026-06-05','Weekly groceries'),
('food','Vegetarian',10.00,'2026-06-10','More plant-based');