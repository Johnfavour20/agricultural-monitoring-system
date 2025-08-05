#!/usr/bin/env python3
"""
Smart Agricultural Monitoring System - Flask Backend
Author: Smart Farm Team
Contact: +234 816 984 9839
Email: orders@igboechejohn@gmail.com
"""

# --- Imports ---
from flask import Flask, request, jsonify, render_template_string, redirect, url_for
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
# from flask_bcrypt import Bcrypt
# from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import datetime, timedelta
import os
import json
import requests
import logging
from werkzeug.security import generate_password_hash, check_password_hash
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
# import africastalking # For SMS notifications to Nigerian numbers


# --- Initialization ---
app = Flask(__name__)

# --- Configuration ---
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-string')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# --- Contact Information ---
SUPPORT_PHONE = "+2348169849839"
SUPPORT_EMAIL = "igboechejohn@gmail.com"
BUSINESS_NAME = "Smart Farm Nigeria"

# --- Initialize Extensions ---
db = SQLAlchemy(app)
# bcrypt = Bcrypt(app)
# jwt = JWTManager(app)
CORS(app)

# --- Configure Logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- AfricasTalking SMS configuration (for Nigerian SMS) ---
username = "smartfarm" # Replace with your username
api_key = "your-africastalking-api-key" # Replace with your API key

# africastalking.initialize(username, api_key)
# sms = africastalking.SMS



# --- Database Models ---
class User(db.Model):
    __tablename__ = 'users'
    # Other class attributes here
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    farm_type = db.Column(db.Enum('crop', 'greenhouse', 'livestock', 'mixed', 'organic', name='farm_type_enum'),
                            nullable=False)
    location = db.Column(db.String(200), nullable=False)
    farm_size = db.Column(db.Numeric(10, 2))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                            onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    subscription_type = db.Column(db.Enum('free', 'basic', 'premium', 'enterprise', name='subscription_type_enum'),
                                    default='free')

    # Relationships
    devices = db.relationship('Device', backref='owner', lazy=True, cascade='all,delete-orphan')
    sensor_data = db.relationship('SensorData', backref='user', lazy=True, cascade='all,delete-orphan')
    orders = db.relationship('Order', backref='customer', lazy=True, cascade='all,delete-orphan')

class Device(db.Model):
    __tablename__ = 'devices'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    device_id = db.Column(db.String(50), unique=True, nullable=False)
    device_name = db.Column(db.String(100), nullable=False)
    device_type = db.Column(db.Enum('esp32', 'arduino', 'raspberry_pi', 'custom', name='device_type_enum'),
                             default='esp32')
    firmware_version = db.Column(db.String(20))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    location_name = db.Column(db.String(100))
    latitude = db.Column(db.Numeric(10, 8))
    longitude = db.Column(db.Numeric(11, 8))
    is_active = db.Column(db.Boolean, default=True)
    configuration = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class SensorData(db.Model):
    __tablename__ = 'sensor_data'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    device_id = db.Column(db.String(50), nullable=False)
    temperature = db.Column(db.Numeric(5, 2))
    humidity = db.Column(db.Numeric(5, 2))
    soil_moisture = db.Column(db.Numeric(5, 2))
    light_intensity = db.Column(db.Numeric(8, 2))
    ph_level = db.Column(db.Numeric(4, 2))
    battery_level = db.Column(db.Numeric(5, 2))
    signal_strength = db.Column(db.Integer)
    latitude = db.Column(db.Numeric(10, 8))
    longitude = db.Column(db.Numeric(11, 8))
    weather_temperature = db.Column(db.Numeric(5, 2))
    weather_humidity = db.Column(db.Numeric(5, 2))
    weather_pressure = db.Column(db.Numeric(7, 2))
    weather_description = db.Column(db.String(100))
    compression_ratio = db.Column(db.Numeric(5, 2))
    is_predicted = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    order_number = db.Column(db.String(20), unique=True, nullable=False)
    customer_name = db.Column(db.String(100), nullable=False)
    customer_phone = db.Column(db.String(20), nullable=False)
    customer_email = db.Column(db.String(100), nullable=False)
    order_type = db.Column(db.Enum('starter_kit', 'professional_kit', 'enterprise_kit', 'custom',
                                    'individual_component', name='order_type_enum'), nullable=False)
    items = db.Column(db.JSON, nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(3), default='NGN')
    order_status = db.Column(db.Enum('pending', 'confirmed', 'processing', 'shipped',
                                     'delivered', 'cancelled', name='order_status_enum'), default='pending')
    payment_status = db.Column(db.Enum('pending', 'paid', 'failed', 'refunded', name='payment_status_enum'),
                                default='pending')
    payment_method = db.Column(db.Enum('bank_transfer', 'card', 'mobile_money',
                                         'cash_on_delivery', name='payment_method_enum'), default='bank_transfer')
    shipping_address = db.Column(db.Text, nullable=False)
    tracking_number = db.Column(db.String(50))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                            onupdate=datetime.utcnow)

class Alert(db.Model):
    __tablename__ = 'alerts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    device_id = db.Column(db.String(50))
    alert_type = db.Column(db.String(50), nullable=False)
    severity = db.Column(db.Enum('info', 'warning', 'critical', name='severity_enum'), default='warning')
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    threshold_value = db.Column(db.Numeric(8, 2))
    current_value = db.Column(db.Numeric(8, 2))
    is_read = db.Column(db.Boolean, default=False)
    is_resolved = db.Column(db.Boolean, default=False)
    notification_sent = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)


# --- Utility Functions ---
def send_sms_notification(phone_number, message):
    """Send SMS notification using AfricasTalking for Nigerian numbers"""
    try:
        # Format phone number for Nigeria
        if phone_number.startswith('+234'):
            phone_number = phone_number[1:] # Remove + for AfricasTalking
        elif phone_number.startswith('0'):
            phone_number = '234' + phone_number[1:] # Convert local format
        # response = sms.send(message, [phone_number])
        # logger.info(f"SMS sent to {phone_number}: {response}")
        # return True
        return False # Placeholder since AfricasTalking is commented out
    except Exception as e:
        logger.error(f"Failed to send SMS to {phone_number}: {str(e)}")
        return False

def send_email_notification(to_email, subject, body):
    """Send email notification"""
    try:
        smtp_server = "smtp.gmail.com" # Configure your SMTP server
        smtp_port = 587
        email_user = "igboechejohn@gmail.com" # Your email
        email_password = "your-email-password" # Your email password

        msg = MIMEMultipart()
        msg['From'] = email_user
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        # server.login(email_user, email_password)
        text = msg.as_string()
        # server.sendmail(email_user, to_email, text)
        server.quit()
        logger.info(f"Email sent to {to_email}")
        # return True
        return False # Placeholder since email is commented out
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {str(e)}")
        return False

def notify_order_received(order):
    """Send notifications when order is received"""
    # SMS to customer
    customer_message = f"Hi {order.customer_name}! Your Smart Farm order #{order.order_number} has been received. Total: ₦{order.total_amount}. We'll call you shortly at {order.customer_phone} to confirm details. Thank you! 🌱"
    send_sms_notification(order.customer_phone, customer_message)

    # SMS to admin
    admin_message = f"New Smart Farm order received! Order #{order.order_number} from {order.customer_name} ({order.customer_phone}). Type: {order.order_type}. Amount: ₦{order.total_amount}. Call customer to confirm."
    send_sms_notification(SUPPORT_PHONE, admin_message)

    # Email to customer
    email_subject = f"Order Confirmation - Smart Farm #{order.order_number}"
    email_body = f"""
    <html>
    <body>
    <h2>🌱 Smart Farm Order Confirmation</h2>
    <p>Dear {order.customer_name},</p>
    <p>Thank you for your order! We have received your Smart Farm system order and our team will contact you shortly.</p>
    <div style="background: #f1f8e9; padding: 20px; border-radius: 10px; margin: 20px 0;">
    <h3>Order Details:</h3>
    <p><strong>Order Number:</strong> {order.order_number}</p>
    <p><strong>Order Type:</strong> {order.order_type.replace('_', ' ').title()}</p>
    <p><strong>Total Amount:</strong> ₦{order.total_amount}</p>
    <p><strong>Status:</strong> {order.order_status.title()}</p>
    </div>
    <h3>📞 What Happens Next?</h3>
    <ol>
    <li>Our team will call you at <strong>{order.customer_phone}</strong> within 2 hours</li>
    <li>We'll confirm your order details and shipping address</li>
    <li>Payment instructions will be provided</li>
    <li>Your hardware will be shipped within 1-3 business days</li>
    </ol>
    <div style="background: #4caf50; color: white; padding: 15px; border-radius: 8px; margin: 20px 0;">
    <h3>📞 Need Immediate Help?</h3>
    <p><strong>Call/WhatsApp:</strong> {SUPPORT_PHONE}</p>
    <p><strong>Email:</strong> {SUPPORT_EMAIL}</p>
    <p><strong>Business Hours:</strong> Mon-Sat 8AM-8PM, Sun 10AM-6PM</p>
    </div>
    <p>Thank you for choosing Smart Farm Nigeria!</p>
    <p>Best regards,<br>Smart Farm Team</p>
    </body>
    </html>
    """
    send_email_notification(order.customer_email, email_subject, email_body)

def get_weather_data(lat, lng):
    """Get weather data from OpenWeatherMap API"""
    try:
        api_key = os.environ.get('OPENWEATHER_API_KEY', 'your-api-key')
        url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lng}&appid={api_key}&units=metric"
        response = requests.get(url, timeout=10)
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        logger.error(f"Weather API error: {str(e)}")
        return None

def calculate_compression_ratio(device_id, new_data):
    """Calculate data compression ratio based on predictive algorithm"""
    try:
        # Get last reading for comparison
        last_reading = SensorData.query.filter_by(device_id=device_id).order_by(SensorData.timestamp.desc()).first()

        if not last_reading:
            return 0.0, False # No compression for first reading

        # Check if values are within prediction thresholds
        temp_diff = abs(float(last_reading.temperature or 0) - float(new_data.get('temperature', 0)))
        humidity_diff = abs(float(last_reading.humidity or 0) - float(new_data.get('humidity', 0)))
        moisture_diff = abs(float(last_reading.soil_moisture or 0) - float(new_data.get('soil_moisture', 0)))
        light_diff = abs(float(last_reading.light_intensity or 0) - float(new_data.get('light_intensity', 0)))

        # Define thresholds for prediction
        if (temp_diff < 1.0 and humidity_diff < 2.0 and
            moisture_diff < 1.5 and light_diff < 50):
            return 85.0, True # High compression - data was predicted
        else:
            return 65.0, False # Lower compression - actual transmission needed
    except Exception as e:
        logger.error(f"Compression calculation error: {str(e)}")
        return 0.0, False

def check_sensor_alerts(user_id, device_id, sensor_data):
    """Check sensor data against thresholds and create alerts"""
    try:
        user = User.query.get(user_id)
        if not user:
            return

        # Default thresholds
        thresholds = {
            'temperature_min': 5,
            'temperature_max': 35,
            'moisture_min': 30,
            'moisture_max': 80,
            'humidity_min': 40,
            'humidity_max': 90
        }

        alerts_to_create = []

        # Check temperature
        if sensor_data.temperature:
            temp = float(sensor_data.temperature)
            if temp < thresholds['temperature_min']:
                alerts_to_create.append({
                    'type': 'temperature_low',
                    'severity': 'warning',
                    'title': 'Low Temperature Alert',
                    'message': f'Temperature dropped to {temp}°C, below minimum threshold of {thresholds["temperature_min"]}°C',
                    'current_value': temp,
                    'threshold_value': thresholds['temperature_min']
                })
            elif temp > thresholds['temperature_max']:
                alerts_to_create.append({
                    'type': 'temperature_high',
                    'severity': 'critical',
                    'title': 'High Temperature Alert',
                    'message': f'Temperature rose to {temp}°C, above maximum threshold of {thresholds["temperature_max"]}°C',
                    'current_value': temp,
                    'threshold_value': thresholds['temperature_max']
                })

        # Check soil moisture
        if sensor_data.soil_moisture:
            moisture = float(sensor_data.soil_moisture)
            if moisture < thresholds['moisture_min']:
                alerts_to_create.append({
                    'type': 'moisture_low',
                    'severity': 'critical',
                    'title': 'Low Soil Moisture Alert',
                    'message': f'Soil moisture at {moisture}%, below minimum threshold. Irrigation recommended.',
                    'current_value': moisture,
                    'threshold_value': thresholds['moisture_min']
                })

        # Create alerts and send notifications
        for alert_data in alerts_to_create:
            alert = Alert(
                user_id=user_id,
                device_id=device_id,
                alert_type=alert_data['type'],
                severity=alert_data['severity'],
                title=alert_data['title'],
                message=alert_data['message'],
                current_value=alert_data['current_value'],
                threshold_value=alert_data['threshold_value']
            )
            db.session.add(alert)

            # Send SMS notification for critical alerts
            if alert_data['severity'] == 'critical':
                sms_message = f"🚨 Smart Farm Alert: {alert_data['title']} - {alert_data['message']} Call {SUPPORT_PHONE} for help."
                send_sms_notification(user.phone, sms_message)

        if alerts_to_create:
            db.session.commit()
            logger.info(f"Created {len(alerts_to_create)} alerts for user {user_id}")

    except Exception as e:
        logger.error(f"Alert checking error: {str(e)}")


# --- API Routes ---

@app.route('/')
def index():
    """Serve the main HTML page"""
    return render_template('index.html')
        

@app.route('/api/register', methods=['POST'])
def register():
    """Register a new farmer"""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['name', 'email', 'phone', 'password', 'farm_type', 'location']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'{field} is required'}), 400

        # Check if user already exists
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already registered'}), 400

        # Validate phone number format
        phone = data['phone'].strip()
        if not phone.startswith('+') or len(phone) < 10:
            return jsonify({'error': 'Please provide a valid phone number with country code'}), 400

        # Create new user
        user = User(
            name=data['name'],
            email=data['email'],
            phone=phone,
            password_hash=generate_password_hash(data['password']),
            farm_type=data['farm_type'],
            location=data['location'],
            farm_size=data.get('farm_size')
        )
        db.session.add(user)
        db.session.commit()

        # Send welcome SMS
        welcome_message = f"Welcome to Smart Farm Nigeria, {data['name']}! Your account has been created. Call {SUPPORT_PHONE} for hardware setup assistance. Happy farming! 🌱"
        send_sms_notification(phone, welcome_message)

        logger.info(f"New user registered: {data['email']} ({phone})")
        return jsonify({
            'message': 'Registration successful',
            'user_id': user.id,
            'support_phone': SUPPORT_PHONE
        }), 201
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return jsonify({'error': 'Registration failed'}), 500

@app.route('/api/login', methods=['POST'])
def login():
    """Login farmer"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({'error': 'Email and password required'}), 400

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            # access_token = create_access_token(identity=user.id)
            return jsonify({
                # 'access_token': access_token,
                'user': {
                    'id': user.id,
                    'name': user.name,
                    'email': user.email,
                    'phone': user.phone,
                    'farm_type': user.farm_type,
                    'location': user.location,
                    'farm_size': float(user.farm_size) if user.farm_size else None
                }
            }), 200

        return jsonify({'error': 'Invalid credentials'}), 401
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'error': 'Login failed'}), 500

@app.route('/api/sensor-data', methods=['POST'])
def receive_sensor_data():
    """Receive sensor data from IoT devices"""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['device_id', 'user_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400

        # Get weather data if location provided
        weather_data = None
        if 'latitude' in data and 'longitude' in data:
            weather_data = get_weather_data(data['latitude'], data['longitude'])

        # Calculate compression ratio
        compression_ratio, is_predicted = calculate_compression_ratio(data['device_id'], data)

        # Create sensor data record
        sensor_record = SensorData(
            user_id=data['user_id'],
            device_id=data['device_id'],
            temperature=data.get('temperature'),
            humidity=data.get('humidity'),
            soil_moisture=data.get('soil_moisture'),
            light_intensity=data.get('light_intensity'),
            ph_level=data.get('ph_level'),
            battery_level=data.get('battery_level'),
            signal_strength=data.get('signal_strength'),
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            weather_temperature=weather_data.get('main', {}).get('temp') if weather_data else None,
            weather_humidity=weather_data.get('main', {}).get('humidity') if weather_data else None,
            weather_pressure=weather_data.get('main', {}).get('pressure') if weather_data else None,
            weather_description=weather_data.get('weather', [{}])[0].get('description') if weather_data else None,
            compression_ratio=compression_ratio,
            is_predicted=is_predicted
        )
        db.session.add(sensor_record)

        # Update device last_seen
        device = Device.query.filter_by(device_id=data['device_id']).first()
        if device:
            device.last_seen = datetime.utcnow()

        db.session.commit()

        # Check for alerts
        check_sensor_alerts(data['user_id'], data['device_id'], sensor_record)

        return jsonify({
            'message': 'Data received successfully',
            'compression_ratio': float(compression_ratio),
            'is_predicted': is_predicted,
            'weather_included': weather_data is not None
        }), 200
    except Exception as e:
        logger.error(f"Sensor data error: {str(e)}")
        return jsonify({'error': 'Failed to process sensor data'}), 500

@app.route('/api/orders', methods=['POST'])
def create_order():
    """Create a new hardware order"""
    try:
        data = request.get_json()

        # Generate order number
        order_number = f"SF{datetime.now().strftime('%Y%m%d')}{Order.query.count() + 1:04d}"

        # Create order
        order = Order(
            user_id=data.get('user_id'),
            order_number=order_number,
            customer_name=data['customer_name'],
            customer_phone=data['customer_phone'],
            customer_email=data['customer_email'],
            order_type=data['order_type'],
            items=data['items'],
            total_amount=data['total_amount'],
            shipping_address=data['shipping_address'],
            notes=data.get('notes', '')
        )
        db.session.add(order)
        db.session.commit()

        # Send notifications
        notify_order_received(order)

        logger.info(f"New order created: {order_number} from {data['customer_phone']}")
        return jsonify({
            'message': 'Order created successfully',
            'order_number': order_number,
            'support_phone': SUPPORT_PHONE,
            'estimated_delivery': (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d')
        }), 201
    except Exception as e:
        logger.error(f"Order creation error: {str(e)}")
        return jsonify({'error': 'Failed to create order'}), 500

@app.route('/api/orders/<order_number>', methods=['GET'])
def get_order_status(order_number):
    """Get order status"""
    try:
        order = Order.query.filter_by(order_number=order_number).first()
        if not order:
            return jsonify({'error': 'Order not found'}), 404

        return jsonify({
            'order_number': order.order_number,
            'status': order.order_status,
            'payment_status': order.payment_status,
            'tracking_number': order.tracking_number,
            'created_at': order.created_at.isoformat(),
            'updated_at': order.updated_at.isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Order status error: {str(e)}")
        return jsonify({'error': 'Failed to get order status'}), 500

@app.route('/api/dashboard/<int:user_id>', methods=['GET'])
# @jwt_required()
def get_dashboard_data(user_id):
    """Get dashboard data for user"""
    try:
        # current_user_id = get_jwt_identity()
        # if current_user_id != user_id:
        #     return jsonify({'error': 'Unauthorized'}), 403

        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Get latest sensor data
        latest_data = db.session.query(SensorData).filter_by(user_id=user_id).order_by(SensorData.timestamp.desc()).limit(10).all()

        # Get device status
        devices = Device.query.filter_by(user_id=user_id).all()

        # Get unread alerts
        alerts = Alert.query.filter_by(user_id=user_id, is_read=False).order_by(Alert.created_at.desc()).limit(5).all()

        # Calculate compression statistics
        avg_compression = db.session.query(db.func.avg(SensorData.compression_ratio)).filter_by(user_id=user_id).scalar() or 0

        return jsonify({
            'user': {
                'name': user.name,
                'phone': user.phone,
                'farm_type': user.farm_type,
                'location': user.location
            },
            'sensor_data': [{
                'device_id': data.device_id,
                'temperature': float(data.temperature) if data.temperature else None,
                'humidity': float(data.humidity) if data.humidity else None,
                'soil_moisture': float(data.soil_moisture) if data.soil_moisture else None,
                'light_intensity': float(data.light_intensity) if data.light_intensity else None,
                'compression_ratio': float(data.compression_ratio) if data.compression_ratio else None,
                'timestamp': data.timestamp.isoformat()
            } for data in latest_data],
            'devices': [{
                'device_id': device.device_id,
                'device_name': device.device_name,
                'is_active': device.is_active,
                'last_seen': device.last_seen.isoformat(),
                'location_name': device.location_name
            } for device in devices],
            'alerts': [{
                'title': alert.title,
                'message': alert.message,
                'severity': alert.severity,
                'created_at': alert.created_at.isoformat()
            } for alert in alerts],
            'statistics': {
                'avg_compression_ratio': float(avg_compression),
                'total_devices': len(devices),
                'active_devices': len([d for d in devices if d.is_active]),
                'unread_alerts': len(alerts)
            },
            'support_contact': SUPPORT_PHONE
        }), 200
    except Exception as e:
        logger.error(f"Dashboard error: {str(e)}")
        return jsonify({'error': 'Failed to load dashboard data'}), 500


# --- Contact and Support Routes ---

@app.route('/api/contact', methods=['POST'])
def contact_support():
    """Handle contact form submissions"""
    try:
        data = request.get_json()

        # Send notification to support team
        support_message = f"Smart Farm contact form: {data.get('name')} ({data.get('phone')}) - {data.get('message')[:100]}..."
        send_sms_notification(SUPPORT_PHONE, support_message)

        # Send confirmation to customer
        if data.get('phone'):
            customer_message = f"Hi {data.get('name')}! We received your message. Our team will call you at {data.get('phone')} within 2 hours. For urgent help, call {SUPPORT_PHONE}. - Smart Farm Team"
            send_sms_notification(data.get('phone'), customer_message)

        return jsonify({
            'message': 'Message sent successfully',
            'support_phone': SUPPORT_PHONE
        }), 200
    except Exception as e:
        logger.error(f"Contact error: {str(e)}")
        return jsonify({'error': 'Failed to send message'}), 500

@app.route('/api/quote', methods=['POST'])
def request_quote():
    """Handle quote requests"""
    try:
        data = request.get_json()

        # Send quote request to sales team
        quote_message = f"Quote request from {data.get('name')} ({data.get('phone')}): {data.get('farm_type')} farm, {data.get('farm_size')} hectares. Requirements: {data.get('requirements', 'Not specified')[:100]}..."
        send_sms_notification(SUPPORT_PHONE, quote_message)

        # Send confirmation to customer
        customer_message = f"Hi {data.get('name')}! We'll prepare a custom quote for your {data.get('farm_type')} farm and call you at {data.get('phone')} today. For immediate help, call {SUPPORT_PHONE}. - Smart Farm Team"
        send_sms_notification(data.get('phone'), customer_message)

        return jsonify({
            'message': 'Quote request submitted successfully',
            'support_phone': SUPPORT_PHONE,
            'response_time': '2-4 hours'
        }), 200
    except Exception as e:
        logger.error(f"Quote request error: {str(e)}")
        return jsonify({'error': 'Failed to submit quote request'}), 500

# --- Health check endpoint ---
@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'support_contact': SUPPORT_PHONE
    })


# --- Error Handlers ---
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error', 'support_phone': SUPPORT_PHONE}), 500

# --- Database Initialization ---
@app.cli.command('create-db')
def create_db_command():
    """Creates the database tables."""
    with app.app_context():
        db.create_all()
    print("Database tables created successfully!")
    logger.info("Database tables created successfully")

# --- Main ---
if __name__ == '__main__':
    # Development server
    print(f"🌱 Smart Farm Nigeria API Server")
    print(f"📞 Support: {SUPPORT_PHONE}")
    print(f"📧 Email: {SUPPORT_EMAIL}")
    print(f"🚀 Starting server...")
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=os.environ.get('FLASK_ENV') == 'development'
    )
