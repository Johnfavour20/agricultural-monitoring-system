-- Smart Agricultural Monitoring System Database Schema
-- MySQL Database Setup

CREATE DATABASE IF NOT EXISTS smart_farm_db;
USE smart_farm_db;
CREATE USER 'smartfarm_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON smart_farm_db.* TO 'smartfarm_user'@'localhost';
FLUSH PRIVILEGES;

-- Users table (farmers registration with phone numbers)
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20) NOT NULL, -- Phone number for order notifications
    password_hash VARCHAR(255) NOT NULL,
    farm_type ENUM('crop', 'greenhouse', 'livestock', 'mixed', 'organic') NOT NULL,
    location VARCHAR(200) NOT NULL,
    farm_size DECIMAL(10,2), -- Farm size in hectares
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    subscription_type ENUM('free', 'basic', 'premium', 'enterprise') DEFAULT 'free'
);

-- Sensor data table
CREATE TABLE sensor_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    device_id VARCHAR(50) NOT NULL,
    temperature DECIMAL(5,2),
    humidity DECIMAL(5,2),
    soil_moisture DECIMAL(5,2),
    light_intensity DECIMAL(8,2),
    ph_level DECIMAL(4,2),
    nitrogen_level DECIMAL(6,2),
    phosphorus_level DECIMAL(6,2),
    potassium_level DECIMAL(6,2),
    battery_level DECIMAL(5,2),
    signal_strength INT,
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),
    weather_temperature DECIMAL(5,2),
    weather_humidity DECIMAL(5,2),
    weather_pressure DECIMAL(7,2),
    weather_description VARCHAR(100),
    compression_ratio DECIMAL(5,2), -- Data compression percentage
    is_predicted BOOLEAN DEFAULT FALSE, -- Whether data was predicted vs actual
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_timestamp (user_id, timestamp),
    INDEX idx_device_timestamp (device_id, timestamp)
);

-- Device management table
CREATE TABLE devices (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    device_id VARCHAR(50) UNIQUE NOT NULL,
    device_name VARCHAR(100) NOT NULL,
    device_type ENUM('esp32', 'arduino', 'raspberry_pi', 'custom') DEFAULT 'esp32',
    firmware_version VARCHAR(20),
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    location_name VARCHAR(100),
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),
    is_active BOOLEAN DEFAULT TRUE,
    configuration JSON, -- Store device-specific configuration
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Orders table for hardware purchases
CREATE TABLE orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    order_number VARCHAR(20) UNIQUE NOT NULL,
    customer_name VARCHAR(100) NOT NULL,
    customer_phone VARCHAR(20) NOT NULL,
    customer_email VARCHAR(100) NOT NULL,
    order_type ENUM('starter_kit', 'professional_kit', 'enterprise_kit', 'custom', 'individual_component') NOT NULL,
    items JSON NOT NULL, -- Store ordered items as JSON
    total_amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'NGN',
    order_status ENUM('pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled') DEFAULT 'pending',
    payment_status ENUM('pending', 'paid', 'failed', 'refunded') DEFAULT 'pending',
    payment_method ENUM('bank_transfer', 'card', 'mobile_money', 'cash_on_delivery') DEFAULT 'bank_transfer',
    shipping_address TEXT NOT NULL,
    tracking_number VARCHAR(50),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Alerts and notifications table
CREATE TABLE alerts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    device_id VARCHAR(50),
    alert_type ENUM('temperature_high', 'temperature_low', 'humidity_high', 'humidity_low', 
                   'moisture_low', 'moisture_high', 'light_low', 'device_offline', 
                   'battery_low', 'system_error', 'maintenance_due') NOT NULL,
    severity ENUM('info', 'warning', 'critical') DEFAULT 'warning',
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    threshold_value DECIMAL(8,2),
    current_value DECIMAL(8,2),
    is_read BOOLEAN DEFAULT FALSE,
    is_resolved BOOLEAN DEFAULT FALSE,
    notification_sent BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_unread (user_id, is_read),
    INDEX idx_created_at (created_at)
);

-- System settings and configurations
CREATE TABLE user_settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    setting_name VARCHAR(100) NOT NULL,
    setting_value JSON NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_setting (user_id, setting_name)
);

-- Support tickets table
CREATE TABLE support_tickets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    ticket_number VARCHAR(20) UNIQUE NOT NULL,
    subject VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    priority ENUM('low', 'medium', 'high', 'urgent') DEFAULT 'medium',
    status ENUM('open', 'in_progress', 'waiting_customer', 'resolved', 'closed') DEFAULT 'open',
    category ENUM('technical', 'hardware', 'software', 'billing', 'general') DEFAULT 'general',
    assigned_to VARCHAR(100),
    customer_phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- API keys for external services
CREATE TABLE api_keys (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    service_name VARCHAR(50) NOT NULL,
    api_key VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Data compression statistics
CREATE TABLE compression_stats (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    device_id VARCHAR(50) NOT NULL,
    date DATE NOT NULL,
    total_data_points INT DEFAULT 0,
    transmitted_data_points INT DEFAULT 0,
    compression_ratio DECIMAL(5,2), -- Percentage of data saved
    bytes_saved BIGINT DEFAULT 0,
    energy_saved_percent DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_device_date (user_id, device_id, date)
);

-- Insert sample data for testing
INSERT INTO users (name, email, phone, password_hash, farm_type, location, farm_size) VALUES
('John Farmer', 'john@smartfarm.com', '+2348123456789', '$2y$10$example_hash', 'crop', 'Port Harcourt, Rivers State', 10.5),
('Mary Agric', 'mary@farming.ng', '+2347098765432', '$2y$10$example_hash2', 'greenhouse', 'Lagos, Nigeria', 5.2),
('David Ranch', 'david@ranch.com', '+2348169849839', '$2y$10$example_hash3', 'livestock', 'Abuja, FCT', 25.0);

-- Insert sample device data
INSERT INTO devices (user_id, device_id, device_name, device_type, firmware_version, location_name, latitude, longitude) VALUES
(1, 'ESP32_001', 'Main Farm Sensor', 'esp32', '2.1.3', 'Main Field', 4.8156, 7.0498),
(1, 'ESP32_002', 'Greenhouse Monitor', 'esp32', '2.1.3', 'Greenhouse A', 4.8200, 7.0520),
(2, 'ESP32_003', 'Lagos Farm Unit', 'esp32', '2.1.2', 'Farm Section 1', 6.5244, 3.3792);

-- Insert sample sensor data
INSERT INTO sensor_data (user_id, device_id, temperature, humidity, soil_moisture, light_intensity, compression_ratio, weather_temperature, weather_humidity) VALUES
(1, 'ESP32_001', 28.5, 65.2, 45.8, 850.0, 78.5, 29.1, 70.3),
(1, 'ESP32_001', 28.2, 66.1, 44.9, 875.5, 82.1, 29.1, 70.3),
(1, 'ESP32_002', 26.8, 72.3, 55.2, 420.0, 75.8, 29.1, 70.3),
(2, 'ESP32_003', 30.1, 58.7, 38.5, 920.0, 85.2, 31.5, 62.8);

-- Insert sample alert thresholds in user_settings
INSERT INTO user_settings (user_id, setting_name, setting_value) VALUES
(1, 'alert_thresholds', '{"temperature_min": 5, "temperature_max": 35, "moisture_min": 30, "moisture_max": 80, "humidity_min": 40, "humidity_max": 90}'),
(1, 'notification_preferences', '{"email": true, "sms": true, "push": false, "daily_reports": true}'),
(1, 'contact_preferences', '{"primary_phone": "+2348123456789", "emergency_contact": "+2348169849839"}');

-- Create indexes for better performance
CREATE INDEX idx_sensor_data_timestamp ON sensor_data(timestamp);
CREATE INDEX idx_sensor_data_user_device ON sensor_data(user_id, device_id);
CREATE INDEX idx_alerts_user_created ON alerts(user_id, created_at);
CREATE INDEX idx_devices_user_active ON devices(user_id, is_active);
CREATE INDEX idx_orders_status ON orders(order_status, created_at);

-- Create views for common queries
CREATE VIEW latest_sensor_readings AS
SELECT 
    sd.*,
    u.name as farmer_name,
    u.phone as farmer_phone,
    d.device_name,
    d.location_name
FROM sensor_data sd
JOIN users u ON sd.user_id = u.id
JOIN devices d ON sd.device_id = d.device_id
WHERE sd.timestamp = (
    SELECT MAX(timestamp) 
    FROM sensor_data sd2 
    WHERE sd2.device_id = sd.device_id
);

CREATE VIEW user_dashboard_summary AS
SELECT 
    u.id as user_id,
    u.name,
    u.email,
    u.phone,
    u.farm_type,
    u.location,
    u.farm_size,
    COUNT(DISTINCT d.device_id) as total_devices,
    COUNT(DISTINCT CASE WHEN d.last_seen > DATE_SUB(NOW(), INTERVAL 1 HOUR) THEN d.device_id END) as active_devices,
    COUNT(DISTINCT CASE WHEN a.is_read = FALSE THEN a.id END) as unread_alerts,
    COUNT(DISTINCT CASE WHEN a.severity = 'critical' AND a.is_resolved = FALSE THEN a.id END) as critical_alerts
FROM users u
LEFT JOIN devices d ON u.id = d.user_id
LEFT JOIN alerts a ON u.id = a.user_id
WHERE u.is_active = TRUE
GROUP BY u.id;

-- Stored procedures for common operations

DELIMITER //

-- Procedure to insert sensor data with compression calculation
CREATE PROCEDURE InsertSensorData(
    IN p_user_id INT,
    IN p_device_id VARCHAR(50),
    IN p_temperature DECIMAL(5,2),
    IN p_humidity DECIMAL(5,2),
    IN p_soil_moisture DECIMAL(5,2),
    IN p_light_intensity DECIMAL(8,2),
    IN p_weather_temp DECIMAL(5,2),
    IN p_weather_humidity DECIMAL(5,2)
)
BEGIN
    DECLARE v_compression_ratio DECIMAL(5,2) DEFAULT 0;
    DECLARE v_is_predicted BOOLEAN DEFAULT FALSE;
    
    -- Simple compression logic: if values are within threshold of previous reading, mark as predicted
    SELECT 
        CASE 
            WHEN ABS(temperature - p_temperature) < 1.0 
             AND ABS(humidity - p_humidity) < 2.0 
             AND ABS(soil_moisture - p_soil_moisture) < 1.5 
             AND ABS(light_intensity - p_light_intensity) < 50 
            THEN TRUE 
            ELSE FALSE 
        END,
        CASE 
            WHEN ABS(temperature - p_temperature) < 1.0 
             AND ABS(humidity - p_humidity) < 2.0 
             AND ABS(soil_moisture - p_soil_moisture) < 1.5 
             AND ABS(light_intensity - p_light_intensity) < 50 
            THEN 85.0  -- High compression when predicted
            ELSE 65.0  -- Lower compression for actual transmission
        END
    INTO v_is_predicted, v_compression_ratio
    FROM sensor_data 
    WHERE device_id = p_device_id 
    ORDER BY timestamp DESC 
    LIMIT 1;
    
    INSERT INTO sensor_data (
        user_id, device_id, temperature, humidity, soil_moisture, 
        light_intensity, weather_temperature, weather_humidity,
        compression_ratio, is_predicted
    ) VALUES (
        p_user_id, p_device_id, p_temperature, p_humidity, p_soil_moisture,
        p_light_intensity, p_weather_temp, p_weather_humidity,
        v_compression_ratio, v_is_predicted
    );
    
    -- Update device last_seen
    UPDATE devices SET last_seen = NOW() WHERE device_id = p_device_id;
    
END //

-- Procedure to create alerts based on thresholds
CREATE PROCEDURE CheckAndCreateAlerts(
    IN p_user_id INT,
    IN p_device_id VARCHAR(50)
)
BEGIN
    DECLARE v_temp DECIMAL(5,2);
    DECLARE v_humidity DECIMAL(5,2);
    DECLARE v_moisture DECIMAL(5,2);
    DECLARE v_temp_min DECIMAL(5,2) DEFAULT 5;
    DECLARE v_temp_max DECIMAL(5,2) DEFAULT 35;
    DECLARE v_moisture_min DECIMAL(5,2) DEFAULT 30;
    DECLARE v_moisture_max DECIMAL(5,2) DEFAULT 80;
    
    -- Get latest sensor readings
    SELECT temperature, humidity, soil_moisture
    INTO v_temp, v_humidity, v_moisture
    FROM sensor_data 
    WHERE user_id = p_user_id AND device_id = p_device_id
    ORDER BY timestamp DESC LIMIT 1;
    
    -- Get user thresholds
    SELECT 
        JSON_EXTRACT(setting_value, '$.temperature_min'),
        JSON_EXTRACT(setting_value, '$.temperature_max'),
        JSON_EXTRACT(setting_value, '$.moisture_min'),
        JSON_EXTRACT(setting_value, '$.moisture_max')
    INTO v_temp_min, v_temp_max, v_moisture_min, v_moisture_max
    FROM user_settings 
    WHERE user_id = p_user_id AND setting_name = 'alert_thresholds';
    
    -- Check temperature alerts
    IF v_temp < v_temp_min THEN
        INSERT INTO alerts (user_id, device_id, alert_type, severity, title, message, threshold_value, current_value)
        VALUES (p_user_id, p_device_id, 'temperature_low', 'warning', 
                'Low Temperature Alert', 
                CONCAT('Temperature has dropped to ', v_temp, '°C, below the minimum threshold of ', v_temp_min, '°C'),
                v_temp_min, v_temp);
    END IF;
    
    IF v_temp > v_temp_max THEN
        INSERT INTO alerts (user_id, device_id, alert_type, severity, title, message, threshold_value, current_value)
        VALUES (p_user_id, p_device_id, 'temperature_high', 'warning',
                'High Temperature Alert',
                CONCAT('Temperature has risen to ', v_temp, '°C, above the maximum threshold of ', v_temp_max, '°C'),
                v_temp_max, v_temp);
    END IF;
    
    -- Check moisture alerts
    IF v_moisture < v_moisture_min THEN
        INSERT INTO alerts (user_id, device_id, alert_type, severity, title, message, threshold_value, current_value)
        VALUES (p_user_id, p_device_id, 'moisture_low', 'critical',
                'Low Soil Moisture Alert',
                CONCAT('Soil moisture is at ', v_moisture, '%, below the minimum threshold of ', v_moisture_min, '%. Irrigation recommended.'),
                v_moisture_min, v_moisture);
    END IF;
    
END //

DELIMITER ;

-- Contact information and support details
-- Primary Support: +234 816 984 9839
-- Email: orders@smartfarm.ng
-- This database supports the Smart Agricultural Monitoring System
-- with comprehensive farmer data, phone number collection, and order management