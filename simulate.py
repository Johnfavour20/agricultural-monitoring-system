#!/usr/bin/env python3
"""
Smart Agricultural Monitoring System - IoT Sensor Simulation
This script simulates real IoT sensor data for testing the Smart Farm system
Author: Smart Farm Team
Contact: +234 816 984 9839
Email: orders@smartfarm.ng
"""

import requests
import json
import time
import random
import math
from datetime import datetime, timedelta
import argparse
import sys
import logging
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
API_BASE_URL = "http://localhost:5000"  # Change to your server URL
SUPPORT_PHONE = "+2348169849839"

class SmartFarmSimulator:
    """Simulates IoT sensors for Smart Farm system"""
    
    def __init__(self, api_url: str = API_BASE_URL):
        self.api_url = api_url
        self.devices = []
        self.weather_cache = {}
        self.simulation_start_time = datetime.now()
        
        # Nigerian locations for testing
        self.locations = [
            {"name": "Port Harcourt, Rivers", "lat": 4.8156, "lng": 7.0498},
            {"name": "Lagos, Nigeria", "lat": 6.5244, "lng": 3.3792},
            {"name": "Abuja, FCT", "lat": 9.0765, "lng": 7.3986},
            {"name": "Kano, Nigeria", "lat": 12.0022, "lng": 8.5920},
            {"name": "Ibadan, Oyo", "lat": 7.3775, "lng": 3.9470},
            {"name": "Kaduna, Nigeria", "lat": 10.5222, "lng": 7.4383},
            {"name": "Enugu, Nigeria", "lat": 6.5244, "lng": 7.5102},
            {"name": "Jos, Plateau", "lat": 9.8965, "lng": 8.8583}
        ]
        
        # Farm types and their characteristics
        self.farm_types = {
            "crop": {
                "temp_range": (20, 35),
                "humidity_range": (40, 80),
                "moisture_range": (30, 70),
                "light_range": (200, 1200),
                "ph_range": (6.0, 7.5)
            },
            "greenhouse": {
                "temp_range": (18, 28),
                "humidity_range": (60, 85),
                "moisture_range": (50, 80),
                "light_range": (300, 800),
                "ph_range": (5.5, 7.0)
            },
            "livestock": {
                "temp_range": (15, 30),
                "humidity_range": (45, 75),
                "moisture_range": (20, 60),
                "light_range": (100, 900),
                "ph_range": (6.5, 8.0)
            }
        }
    
    def create_test_devices(self, num_devices: int = 3) -> List[Dict]:
        """Create test devices with different characteristics"""
        devices = []
        
        for i in range(num_devices):
            location = random.choice(self.locations)
            farm_type = random.choice(list(self.farm_types.keys()))
            
            device = {
                "device_id": f"ESP32_SIM_{i+1:03d}",
                "user_id": 1,  # Default test user
                "device_name": f"Smart Farm Sensor {i+1}",
                "farm_type": farm_type,
                "location": location,
                "latitude": location["lat"] + random.uniform(-0.01, 0.01),
                "longitude": location["lng"] + random.uniform(-0.01, 0.01),
                "firmware_version": "2.1.3",
                "battery_level": random.uniform(80, 100),
                "signal_strength": random.randint(-70, -30),
                "last_values": {}  # Store previous values for realistic changes
            }
            devices.append(device)
            
        self.devices = devices
        logger.info(f"Created {len(devices)} test devices")
        return devices
    
    def simulate_realistic_sensor_data(self, device: Dict) -> Dict:
        """Generate realistic sensor data based on time, location, and farm type"""
        current_time = datetime.now()
        hour = current_time.hour
        
        # Get farm characteristics
        farm_chars = self.farm_types[device["farm_type"]]
        
        # Simulate daily temperature cycle
        base_temp = (farm_chars["temp_range"][0] + farm_chars["temp_range"][1]) / 2
        temp_variation = (farm_chars["temp_range"][1] - farm_chars["temp_range"][0]) / 4
        
        # Temperature follows a sine wave with peak at 14:00
        temp_cycle = math.sin((hour - 6) * math.pi / 12) if 6 <= hour <= 18 else -0.3
        temperature = base_temp + (temp_cycle * temp_variation) + random.uniform(-2, 2)
        
        # Humidity inversely related to temperature
        base_humidity = (farm_chars["humidity_range"][0] + farm_chars["humidity_range"][1]) / 2
        humidity = base_humidity - (temperature - base_temp) * 1.5 + random.uniform(-5, 5)
        humidity = max(farm_chars["humidity_range"][0], min(farm_chars["humidity_range"][1], humidity))
        
        # Soil moisture varies slowly
        if "soil_moisture" in device["last_values"]:
            moisture_change = random.uniform(-2, 1)  # Slight tendency to dry out
            soil_moisture = device["last_values"]["soil_moisture"] + moisture_change
        else:
            soil_moisture = random.uniform(*farm_chars["moisture_range"])
        
        soil_moisture = max(farm_chars["moisture_range"][0], min(farm_chars["moisture_range"][1], soil_moisture))
        
        # Light intensity based on time of day
        if 6 <= hour <= 18:
            base_light = farm_chars["light_range"][1]
            light_cycle = math.sin((hour - 6) * math.pi / 12)
            light_intensity = base_light * light_cycle * random.uniform(0.8, 1.2)
        else:
            light_intensity = random.uniform(0, 50)  # Night time
        
        # pH changes slowly
        if "ph_level" in device["last_values"]:
            ph_change = random.uniform(-0.1, 0.1)
            ph_level = device["last_values"]["ph_level"] + ph_change
        else:
            ph_level = random.uniform(*farm_chars["ph_range"])
        
        ph_level = max(farm_chars["ph_range"][0], min(farm_chars["ph_range"][1], ph_level))
        
        # Battery level decreases slowly
        if "battery_level" in device["last_values"]:
            battery_decrease = random.uniform(0, 0.5)  # 0-0.5% per reading
            device["battery_level"] = max(10, device["battery_level"] - battery_decrease)
        
        # Signal strength varies
        base_signal = device["signal_strength"]
        signal_strength = base_signal + random.randint(-10, 10)
        signal_strength = max(-100, min(-20, signal_strength))
        
        # Nitrogen, Phosphorus, Potassium levels (NPK)
        nitrogen = random.uniform(20, 200)  # mg/kg
        phosphorus = random.uniform(10, 100)  # mg/kg
        potassium = random.uniform(50, 300)  # mg/kg
        
        sensor_data = {
            "device_id": device["device_id"],
            "user_id": device["user_id"],
            "temperature": round(temperature, 1),
            "humidity": round(humidity, 1),
            "soil_moisture": round(soil_moisture, 1),
            "light_intensity": round(light_intensity, 1),
            "ph_level": round(ph_level, 2),
            "nitrogen_level": round(nitrogen, 1),
            "phosphorus_level": round(phosphorus, 1),
            "potassium_level": round(potassium, 1),
            "battery_level": round(device["battery_level"], 1),
            "signal_strength": signal_strength,
            "latitude": device["latitude"],
            "longitude": device["longitude"],
            "timestamp": current_time.isoformat()
        }
        
        # Store current values for next iteration
        device["last_values"] = {
            "temperature": temperature,
            "humidity": humidity,
            "soil_moisture": soil_moisture,
            "light_intensity": light_intensity,
            "ph_level": ph_level,
            "battery_level": device["battery_level"]
        }
        
        return sensor_data
    
    def send_sensor_data(self, sensor_data: Dict) -> bool:
        """Send sensor data to the API"""
        try:
            url = f"{self.api_url}/api/sensor-data"
            headers = {"Content-Type": "application/json"}
            
            response = requests.post(url, json=sensor_data, headers=headers, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                compression_ratio = result.get("compression_ratio", 0)
                is_predicted = result.get("is_predicted", False)
                
                logger.info(f"✅ Data sent from {sensor_data['device_id']}: "
                          f"Temp={sensor_data['temperature']}°C, "
                          f"Moisture={sensor_data['soil_moisture']}%, "
                          f"Compression={compression_ratio}% "
                          f"{'(Predicted)' if is_predicted else '(Transmitted)'}")
                return True
            else:
                logger.error(f"❌ Failed to send data: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Network error sending sensor data: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"❌ Error sending sensor data: {str(e)}")
            return False
    
    def simulate_device_issues(self, device: Dict) -> Optional[Dict]:
        """Simulate occasional device issues"""
        # 5% chance of device issues
        if random.random() < 0.05:
            issue_type = random.choice(["offline", "low_battery", "sensor_error"])
            
            if issue_type == "offline":
                logger.warning(f"⚠️ Device {device['device_id']} went offline")
                return None
            elif issue_type == "low_battery":
                device["battery_level"] = random.uniform(5, 15)
                logger.warning(f"🔋 Device {device['device_id']} low battery: {device['battery_level']}%")
            elif issue_type == "sensor_error":
                # Return invalid data to test error handling
                logger.warning(f"⚠️ Device {device['device_id']} sensor error")
                return {
                    "device_id": device["device_id"],
                    "user_id": device["user_id"],
                    "temperature": None,
                    "humidity": None,
                    "soil_moisture": None,
                    "error": "Sensor malfunction detected"
                }
        
        return self.simulate_realistic_sensor_data(device)
    
    def create_test_user(self) -> bool:
        """Create a test user for simulation"""
        try:
            user_data = {
                "name": "Test Farmer Simulation",
                "email": "test@smartfarm.ng",
                "phone": "+2348000000001",
                "password": "testpass123",
                "farm_type": "crop",
                "location": "Port Harcourt, Rivers State",
                "farm_size": 15.5
            }
            
            url = f"{self.api_url}/api/register"
            response = requests.post(url, json=user_data, timeout=10)
            
            if response.status_code == 201:
                logger.info("✅ Test user created successfully")
                return True
            elif response.status_code == 400 and "already registered" in response.text:
                logger.info("ℹ️ Test user already exists")
                return True
            else:
                logger.error(f"❌ Failed to create test user: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error creating test user: {str(e)}")
            return False
    
    def test_order_system(self) -> bool:
        """Test the order system"""
        try:
            order_data = {
                "user_id": 1,
                "customer_name": "Test Customer",
                "customer_phone": "+2348000000002",
                "customer_email": "testorder@smartfarm.ng",
                "order_type": "starter_kit",
                "items": [
                    {"name": "ESP32 Development Board", "quantity": 1, "price": 12000},
                    {"name": "DHT22 Sensor", "quantity": 1, "price": 3500},
                    {"name": "Soil Moisture Sensor", "quantity": 2, "price": 2500},
                    {"name": "BH1750 Light Sensor", "quantity": 1, "price": 2000}
                ],
                "total_amount": 22500,
                "shipping_address": "123 Test Farm Road, Port Harcourt, Rivers State"
            }
            
            url = f"{self.api_url}/api/orders"
            response = requests.post(url, json=order_data, timeout=10)
            
            if response.status_code == 201:
                result = response.json()
                logger.info(f"✅ Test order created: {result['order_number']}")
                logger.info(f"📞 Support contact: {result['support_phone']}")
                return True
            else:
                logger.error(f"❌ Failed to create test order: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error testing order system: {str(e)}")
            return False
    
    def run_simulation(self, duration_minutes: int = 60, interval_seconds: int = 30, 
                      test_orders: bool = False, create_user: bool = True):
        """Run the complete simulation"""
        logger.info(f"🌱 Starting Smart Farm IoT Simulation")
        logger.info(f"📞 Support Contact: {SUPPORT_PHONE}")
        logger.info(f"⏱️ Duration: {duration_minutes} minutes")
        logger.info(f"📡 Data interval: {interval_seconds} seconds")
        logger.info(f"🎯 API URL: {self.api_url}")
        
        # Test API connectivity
        try:
            response = requests.get(f"{self.api_url}/health", timeout=10)
            if response.status_code == 200:
                logger.info("✅ API server is responsive")
            else:
                logger.error("❌ API server not responding correctly")
                return False
        except Exception as e:
            logger.error(f"❌ Cannot connect to API server: {str(e)}")
            logger.info(f"💡 Make sure the Flask app is running on {self.api_url}")
            return False
        
        # Create test user if requested
        if create_user:
            if not self.create_test_user():
                logger.warning("⚠️ Could not create test user, continuing anyway...")
        
        # Test order system if requested
        if test_orders:
            logger.info("🛒 Testing order system...")
            self.test_order_system()
        
        # Create test devices
        self.create_test_devices()
        
        # Display device information
        logger.info("📱 Created test devices:")
        for device in self.devices:
            logger.info(f"  • {device['device_id']}: {device['device_name']} "
                       f"({device['farm_type']} farm at {device['location']['name']})")
        
        # Run simulation loop
        end_time = datetime.now() + timedelta(minutes=duration_minutes)
        iteration = 0
        successful_transmissions = 0
        total_attempts = 0
        
        logger.info(f"🚀 Starting data simulation...")
        
        try:
            while datetime.now() < end_time:
                iteration += 1
                logger.info(f"\n📊 Simulation Iteration #{iteration}")
                
                for device in self.devices:
                    # Simulate sensor data (with possible issues)
                    sensor_data = self.simulate_device_issues(device)
                    
                    if sensor_data is None:
                        continue  # Device offline
                    
                    # Send data to API
                    total_attempts += 1
                    if self.send_sensor_data(sensor_data):
                        successful_transmissions += 1
                
                # Display statistics
                success_rate = (successful_transmissions / total_attempts * 100) if total_attempts > 0 else 0
                runtime = datetime.now() - self.simulation_start_time
                
                logger.info(f"📈 Statistics: {successful_transmissions}/{total_attempts} successful "
                          f"({success_rate:.1f}% success rate)")
                logger.info(f"⏱️ Runtime: {runtime}")
                
                # Wait for next iteration
                if datetime.now() < end_time:
                    logger.info(f"⏸️ Waiting {interval_seconds} seconds...")
                    time.sleep(interval_seconds)
        
        except KeyboardInterrupt:
            logger.info("\n⏹️ Simulation stopped by user")
        
        except Exception as e:
            logger.error(f"❌ Simulation error: {str(e)}")
        
        finally:
            # Final statistics
            total_runtime = datetime.now() - self.simulation_start_time
            logger.info(f"\n🏁 Simulation Complete!")
            logger.info(f"⏱️ Total runtime: {total_runtime}")
            logger.info(f"📊 Final statistics:")
            logger.info(f"   • Total attempts: {total_attempts}")
            logger.info(f"   • Successful: {successful_transmissions}")
            logger.info(f"   • Success rate: {(successful_transmissions/total_attempts*100) if total_attempts > 0 else 0:.1f}%")
            logger.info(f"   • Devices simulated: {len(self.devices)}")
            logger.info(f"📞 Support: {SUPPORT_PHONE}")

def main():
    """Main function with command line arguments"""
    parser = argparse.ArgumentParser(description="Smart Farm IoT Sensor Simulation")
    parser.add_argument("--url", default=API_BASE_URL, help="API server URL")
    parser.add_argument("--duration", type=int, default=60, help="Simulation duration in minutes")
    parser.add_argument("--interval", type=int, default=30, help="Data transmission interval in seconds")
    parser.add_argument("--devices", type=int, default=3, help="Number of devices to simulate")
    parser.add_argument("--test-orders", action="store_true", help="Test the order system")
    parser.add_argument("--no-user", action="store_true", help="Don't create test user")
    parser.add_argument("--quiet", action="store_true", help="Reduce logging output")
    
    args = parser.parse_args()
    
    # Adjust logging level
    if args.quiet:
        logging.getLogger().setLevel(logging.WARNING)
    
    # Create and run simulator
    simulator = SmartFarmSimulator(api_url=args.url)
    
    # Print banner
    print("=" * 60)
    print("🌱 SMART FARM NIGERIA - IoT SENSOR SIMULATION")
    print("=" * 60)
    print(f"📞 Support: {SUPPORT_PHONE}")
    print(f"📧 Email: orders@smartfarm.ng")
    print(f"🌐 API URL: {args.url}")
    print(f"⏱️ Duration: {args.duration} minutes")
    print(f"📱 Devices: {args.devices}")
    print("=" * 60)
    
    # Create devices
    simulator.create_test_devices(args.devices)
    
    # Run simulation
    simulator.run_simulation(
        duration_minutes=args.duration,
        interval_seconds=args.interval,
        test_orders=args.test_orders,
        create_user=not args.no_user
    )

if __name__ == "__main__":
    main()

# Example usage:
"""
# Basic simulation (1 hour, 3 devices)
python simulate.py

# Custom simulation
python simulate.py --duration 30 --interval 15 --devices 5

# Test with order system
python simulate.py --test-orders --duration 10

# Production server
python simulate.py --url https://api.smartfarm.ng --duration 120

# Quiet mode for automated testing
python simulate.py --quiet --duration 5 --no-user

Commands to install dependencies:
pip install requests

Features demonstrated:
✅ Realistic sensor data simulation
✅ Multiple device types and locations
✅ Daily temperature/light cycles
✅ Gradual changes in soil moisture and pH
✅ Device issues simulation (offline, low battery, errors)
✅ API connectivity testing
✅ Order system testing
✅ Compression ratio tracking
✅ Nigerian phone number integration
✅ Comprehensive logging and statistics

This simulation helps test:
- Real-time data ingestion
- Predictive compression algorithms
- Alert generation systems
- Database performance
- API responsiveness
- SMS notification systems
- Order processing workflows
"""