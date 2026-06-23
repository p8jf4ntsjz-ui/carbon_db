CREATE DATABASE IF NOT EXISTS carbon_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE carbon_db;

CREATE TABLE IF NOT EXISTS companies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    type ENUM('ship_owner','ship_manager','charterer','supplier','other') DEFAULT 'ship_owner',
    country VARCHAR(60),
    industry VARCHAR(100) DEFAULT 'Maritime / Shipping',
    reporting_year INT DEFAULT 2024,
    ghg_boundary ENUM('operational','equity','financial') DEFAULT 'operational',
    base_year INT DEFAULT 2019,
    is_active TINYINT(1) DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(180) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(80) NOT NULL,
    last_name VARCHAR(80) NOT NULL,
    role ENUM('superadmin','admin','manager','analyst','viewer') DEFAULT 'analyst',
    company_id INT,
    is_active TINYINT(1) DEFAULT 1,
    last_login DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS vessels (
    id INT AUTO_INCREMENT PRIMARY KEY,
    company_id INT NOT NULL,
    name VARCHAR(150) NOT NULL,
    imo_number VARCHAR(20) UNIQUE NOT NULL,
    vessel_type ENUM('bulk_carrier','tanker','container','ro_ro','lng_carrier',
                     'general_cargo','cruise','other') DEFAULT 'bulk_carrier',
    flag_state VARCHAR(60),
    gross_tonnage FLOAT,
    dwt FLOAT,
    built_year INT,
    main_engine VARCHAR(100),
    fuel_type ENUM('hfo','vlsfo','mdo','mgo','lng','methanol','ammonia','other') DEFAULT 'vlsfo',
    ownership_type ENUM('owned','leased','chartered_in','chartered_out') DEFAULT 'owned',
    is_active TINYINT(1) DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS emission_categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    scope ENUM('scope1','scope2','scope3') NOT NULL,
    category VARCHAR(50) NOT NULL,
    name VARCHAR(150) NOT NULL,
    description TEXT,
    is_relevant_shipping TINYINT(1) DEFAULT 1
);

CREATE TABLE IF NOT EXISTS emission_factors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    source VARCHAR(100) NOT NULL,
    fuel_type VARCHAR(50),
    activity_type VARCHAR(100),
    region VARCHAR(60) DEFAULT 'global',
    year INT,
    co2_factor FLOAT NOT NULL,
    ch4_factor FLOAT DEFAULT 0,
    n2o_factor FLOAT DEFAULT 0,
    unit VARCHAR(30) NOT NULL,
    gwp_co2 FLOAT DEFAULT 1.0,
    gwp_ch4 FLOAT DEFAULT 27.9,
    gwp_n2o FLOAT DEFAULT 273.0,
    supplier_id INT,
    is_verified TINYINT(1) DEFAULT 0,
    data_quality ENUM('primary','secondary','estimated') DEFAULT 'secondary',
    valid_from DATE,
    valid_to DATE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS suppliers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    company_id INT NOT NULL,
    name VARCHAR(200) NOT NULL,
    type ENUM('fuel_supplier','port','maintenance','logistics','food','waste','other') DEFAULT 'other',
    country VARCHAR(60),
    contact_email VARCHAR(180),
    has_provided_factor TINYINT(1) DEFAULT 0,
    factor_year INT,
    tier INT DEFAULT 1,
    is_active TINYINT(1) DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS voyages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vessel_id INT NOT NULL,
    voyage_number VARCHAR(50) NOT NULL,
    port_departure VARCHAR(100),
    port_arrival VARCHAR(100),
    departure_date DATETIME NOT NULL,
    arrival_date DATETIME,
    distance_nm FLOAT,
    cargo_weight_mt FLOAT,
    fuel_consumed FLOAT,
    fuel_type VARCHAR(20),
    charter_party VARCHAR(100),
    status ENUM('planned','in_progress','completed','cancelled') DEFAULT 'planned',
    notes TEXT,
    created_by INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vessel_id) REFERENCES vessels(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS emissions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    company_id INT NOT NULL,
    vessel_id INT,
    voyage_id INT,
    category_id INT NOT NULL,
    supplier_id INT,
    reporting_year INT NOT NULL,
    reporting_period VARCHAR(20),
    calc_method ENUM('spend_based','average_data','supplier_specific','hybrid','fuel_based') NOT NULL,
    activity_value FLOAT NOT NULL,
    activity_unit VARCHAR(30) NOT NULL,
    emission_factor_id INT,
    emission_factor_value FLOAT,
    emission_factor_unit VARCHAR(50),
    co2_tonnes FLOAT DEFAULT 0,
    ch4_tonnes FLOAT DEFAULT 0,
    n2o_tonnes FLOAT DEFAULT 0,
    total_co2e FLOAT NOT NULL DEFAULT 0,
    data_quality ENUM('primary','secondary','estimated') DEFAULT 'secondary',
    confidence FLOAT DEFAULT 0.8,
    verified TINYINT(1) DEFAULT 0,
    verified_by INT,
    verified_at DATETIME,
    notes TEXT,
    created_by INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
    FOREIGN KEY (vessel_id) REFERENCES vessels(id) ON DELETE SET NULL,
    FOREIGN KEY (category_id) REFERENCES emission_categories(id),
    FOREIGN KEY (emission_factor_id) REFERENCES emission_factors(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS fixture_schedules (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vessel_id INT NOT NULL,
    company_id INT NOT NULL,
    charterer VARCHAR(200),
    fixture_type ENUM('time_charter','voyage_charter','bareboat','contract_of_affreightment') NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    hire_rate FLOAT,
    currency VARCHAR(10) DEFAULT 'USD',
    emission_allocation ENUM('owner','charterer','split') DEFAULT 'charterer',
    owner_pct FLOAT DEFAULT 0,
    charterer_pct FLOAT DEFAULT 100,
    status ENUM('active','expired','cancelled') DEFAULT 'active',
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vessel_id) REFERENCES vessels(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS reports (
    id INT AUTO_INCREMENT PRIMARY KEY,
    company_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    report_type ENUM('annual','quarterly','vessel','custom') DEFAULT 'annual',
    reporting_year INT NOT NULL,
    scope_filter VARCHAR(30) DEFAULT 'all',
    format ENUM('pdf','excel','json','csv') DEFAULT 'json',
    status ENUM('pending','generating','ready','failed') DEFAULT 'pending',
    file_path VARCHAR(255),
    generated_by INT,
    generated_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id)
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    company_id INT,
    entity_type VARCHAR(50) NOT NULL,
    entity_id INT NOT NULL,
    action ENUM('create','update','delete','verify','export') NOT NULL,
    old_value JSON,
    new_value JSON,
    ip_address VARCHAR(45),
    user_agent VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_entity (entity_type, entity_id),
    INDEX idx_created (created_at)
);