-- Smart Agricultural Monitoring System Database Schema
-- PostgreSQL Database Setup

-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    farm_type VARCHAR(20) CHECK (farm_type IN ('crop', 'greenhouse', 'livestock', 'mixed', 'organic')) NOT NULL,
    location VARCHAR(200) NOT NULL,
    farm_size DECIMAL(10,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    subscription_type VARCHAR(20) CHECK (subscription_type IN ('free', 'basic', 'premium', 'enterprise')) DEFAULT 'free'
);

-- Sensor data table
CREATE TABLE sensor_data (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
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
    compression_ratio DECIMAL(5,2),
    is_predicted BOOLEAN DEFAULT FALSE,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_user_timestamp ON sensor_data (user_id, timestamp);
CREATE INDEX idx_device_timestamp ON sensor_data (device_id, timestamp);

-- Device management table
CREATE TABLE devices (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    device_id VARCHAR(50) UNIQUE NOT NULL,
    device_name VARCHAR(100) NOT NULL,
    device_type VARCHAR(20) CHECK (device_type IN ('esp32', 'arduino', 'raspberry_pi', 'custom')) DEFAULT 'esp32',
    firmware_version VARCHAR(20),
    last_seen TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    location_name VARCHAR(100),
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),
    is_active BOOLEAN DEFAULT TRUE,
    configuration JSONB, -- JSONB is PostgreSQL's optimized JSON type
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Orders table for hardware purchases
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    order_number VARCHAR(20) UNIQUE NOT NULL,
    customer_name VARCHAR(100) NOT NULL,
    customer_phone VARCHAR(20) NOT NULL,
    customer_email VARCHAR(100) NOT NULL,
    order_type VARCHAR(50) CHECK (order_type IN ('starter_kit', 'professional_kit', 'enterprise_kit', 'custom', 'individual_component')) NOT NULL,
    items JSONB NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'NGN',
    order_status VARCHAR(20) CHECK (order_status IN ('pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled')) DEFAULT 'pending',
    payment_status VARCHAR(20) CHECK (payment_status IN ('pending', 'paid', 'failed', 'refunded')) DEFAULT 'pending',
    payment_method VARCHAR(20) CHECK (payment_method IN ('bank_transfer', 'card', 'mobile_money', 'cash_on_delivery')) DEFAULT 'bank_transfer',
    shipping_address TEXT NOT NULL,
    tracking_number VARCHAR(50),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Alerts and notifications table
CREATE TABLE alerts (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    device_id VARCHAR(50),
    alert_type VARCHAR(50) CHECK (alert_type IN ('temperature_high', 'temperature_low', 'humidity_high', 'humidity_low',
                   'moisture_low', 'moisture_high', 'light_low', 'device_offline',
                   'battery_low', 'system_error', 'maintenance_due')) NOT NULL,
    severity VARCHAR(10) CHECK (severity IN ('info', 'warning', 'critical')) DEFAULT 'warning',
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    threshold_value DECIMAL(8,2),
    current_value DECIMAL(8,2),
    is_read BOOLEAN DEFAULT FALSE,
    is_resolved BOOLEAN DEFAULT FALSE,
    notification_sent BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP WITH TIME ZONE NULL
);

CREATE INDEX idx_user_unread ON alerts (user_id, is_read);
CREATE INDEX idx_created_at ON alerts (created_at);

-- System settings and configurations
CREATE TABLE user_settings (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    setting_name VARCHAR(100) NOT NULL,
    setting_value JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (user_id, setting_name)
);

-- Support tickets table
CREATE TABLE support_tickets (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    ticket_number VARCHAR(20) UNIQUE NOT NULL,
    subject VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    priority VARCHAR(20) CHECK (priority IN ('low', 'medium', 'high', 'urgent')) DEFAULT 'medium',
    status VARCHAR(20) CHECK (status IN ('open', 'in_progress', 'waiting_customer', 'resolved', 'closed')) DEFAULT 'open',
    category VARCHAR(20) CHECK (category IN ('technical', 'hardware', 'software', 'billing', 'general')) DEFAULT 'general',
    assigned_to VARCHAR(100),
    customer_phone VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP WITH TIME ZONE NULL
);

-- API keys for external services
CREATE TABLE api_keys (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    service_name VARCHAR(50) NOT NULL,
    api_key VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE NULL
);

-- Data compression statistics
CREATE TABLE compression_stats (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    device_id VARCHAR(50) NOT NULL,
    date DATE NOT NULL,
    total_data_points INT DEFAULT 0,
    transmitted_data_points INT DEFAULT 0,
    compression_ratio DECIMAL(5,2),
    bytes_saved BIGINT DEFAULT 0,
    energy_saved_percent DECIMAL(5,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (user_id, device_id, date)
);