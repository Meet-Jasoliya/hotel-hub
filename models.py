from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

# Initialize SQLAlchemy with no settings
db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password_hash = db.Column(db.String(256), nullable=False)
    
    # Role can be: 'superadmin', 'hoteladmin', 'customer'
    role = db.Column(db.String(50), nullable=False, default='customer')
    
    # Relationships
    # If user is a hoteladmin, they can own multiple hotels (or one, we use list to be flexible)
    hotels_owned = db.relationship('Hotel', backref='owner', lazy=True)
    # If user is a customer, they can have multiple bookings
    bookings = db.relationship('Booking', backref='customer', lazy=True)

class Hotel(db.Model):
    __tablename__ = 'hotels'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    address = db.Column(db.String(300), nullable=False)
    
    # Status: 'pending', 'approved', 'rejected' - managed by superadmin
    status = db.Column(db.String(50), nullable=False, default='pending')
    image_path = db.Column(db.String(500), nullable=True)
    
    # Foreign key linking to the hoteladmin who created it
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    rooms = db.relationship('Room', backref='hotel', lazy=True, cascade="all, delete-orphan")
    bookings = db.relationship('Booking', backref='hotel', lazy=True, cascade="all, delete-orphan")
    service_requests = db.relationship('ServiceRequest', backref='hotel', lazy=True, cascade="all, delete-orphan")

class Room(db.Model):
    __tablename__ = 'rooms'
    
    id = db.Column(db.Integer, primary_key=True)
    room_number = db.Column(db.String(50), nullable=False)
    room_type = db.Column(db.String(100), nullable=False) # e.g., 'Single', 'Double', 'Suite'
    price_per_night = db.Column(db.Float, nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    
    # Link to hotel
    hotel_id = db.Column(db.Integer, db.ForeignKey('hotels.id'), nullable=False)
    
    # Relationships
    bookings = db.relationship('Booking', backref='room', lazy=True)

class Booking(db.Model):
    __tablename__ = 'bookings'
    
    id = db.Column(db.Integer, primary_key=True)
    check_in_date = db.Column(db.Date, nullable=False)
    check_out_date = db.Column(db.Date, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    
    # Status can be 'pending', 'active', 'completed', 'cancelled', 'rejected'
    status = db.Column(db.String(50), default='pending')
    identity_proof = db.Column(db.String(500), nullable=True)
    is_accepted_notified = db.Column(db.Boolean, default=False)
    
    # Foreign Keys
    hotel_id = db.Column(db.Integer, db.ForeignKey('hotels.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    service_requests = db.relationship('ServiceRequest', backref='booking', lazy=True)

class ServiceRequest(db.Model):
    __tablename__ = 'service_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    service_type = db.Column(db.String(100), nullable=False) # e.g., 'Food', 'Cleaning', 'Laundry'
    request_details = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Status can be 'pending', 'in_progress', 'completed'
    status = db.Column(db.String(50), default='pending')
    
    # Foreign Keys
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=False)
    hotel_id = db.Column(db.Integer, db.ForeignKey('hotels.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
