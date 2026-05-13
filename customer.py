from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from models import db, Hotel, Room, Booking, ServiceRequest
from functools import wraps
from datetime import datetime
import os
from werkzeug.utils import secure_filename

customer = Blueprint('customer', __name__, url_prefix='/customer')

def customer_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'customer':
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@customer.route('/dashboard')
@customer_required
def dashboard():
    # Check for newly accepted bookings
    newly_accepted = Booking.query.filter_by(customer_id=current_user.id, status='active', is_accepted_notified=False).all()
    for booking in newly_accepted:
        flash(f'Your booking request for {booking.hotel.name} (Room {booking.room.room_number}) has been accepted!', 'success')
        booking.is_accepted_notified = True
    if newly_accepted:
        db.session.commit()
        
    active_bookings = Booking.query.filter_by(customer_id=current_user.id, status='active').all()
    return render_template('customer/dashboard.html', active_bookings=active_bookings)
@customer.route('/hotels')
def find_hotels():
    query = request.args.get('query')
    if query:
        approved_hotels = Hotel.query.filter(Hotel.status == 'approved', Hotel.address.ilike(f'%{query}%')).all()
    else:
        approved_hotels = Hotel.query.filter_by(status='approved').all()
    return render_template('customer/find_hotels.html', hotels=approved_hotels)

@customer.route('/hotel/<int:hotel_id>')
def view_hotel(hotel_id):
    hotel = Hotel.query.get_or_404(hotel_id)
    if hotel.status != 'approved':
        flash('This hotel is not available.', 'danger')
        return redirect(url_for('customer.find_hotels'))
    
    available_rooms = Room.query.filter_by(hotel_id=hotel.id, is_available=True).all()
    return render_template('customer/view_hotel.html', hotel=hotel, rooms=available_rooms)

@customer.route('/book-room/<int:room_id>', methods=['POST'])
@customer_required
def book_room(room_id):
    room = Room.query.get_or_404(room_id)
    if not room.is_available:
        flash('Sorry, this room is no longer available.', 'warning')
        return redirect(url_for('customer.view_hotel', hotel_id=room.hotel_id))
        
    check_in_str = request.form.get('check_in')
    check_out_str = request.form.get('check_out')
    
    identity_proof = request.files.get('identity_proof')
    if not identity_proof or identity_proof.filename == '':
        flash('Identity proof is required.', 'danger')
        return redirect(url_for('customer.view_hotel', hotel_id=room.hotel_id))
    
    try:
        check_in = datetime.strptime(check_in_str, '%Y-%m-%d').date()
        check_out = datetime.strptime(check_out_str, '%Y-%m-%d').date()
        days = (check_out - check_in).days
        if days <= 0:
            flash('Check-out date must be after check-in date.', 'danger')
            return redirect(url_for('customer.view_hotel', hotel_id=room.hotel_id))
            
        total_price = days * room.price_per_night
        
        filename = secure_filename(identity_proof.filename)
        unique_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'identity_proofs')
        os.makedirs(upload_folder, exist_ok=True)
        file_path = os.path.join(upload_folder, unique_filename)
        identity_proof.save(file_path)
        
        db_file_path = f"uploads/identity_proofs/{unique_filename}"
        
        booking = Booking(
            check_in_date=check_in,
            check_out_date=check_out,
            total_price=total_price,
            status='pending',
            identity_proof=db_file_path,
            hotel_id=room.hotel_id,
            room_id=room.id,
            customer_id=current_user.id
        )
        
        # Mark room as unavailable
        room.is_available = False
        
        db.session.add(booking)
        db.session.commit()
        flash('Booking request submitted successfully! Pending Hotel Admin approval.', 'success')
        return redirect(url_for('customer.dashboard'))
        
    except ValueError:
        flash('Invalid date format.', 'danger')
        return redirect(url_for('customer.view_hotel', hotel_id=room.hotel_id))

@customer.route('/my-bookings')
@customer_required
def my_bookings():
    bookings = Booking.query.filter_by(customer_id=current_user.id).order_by(Booking.id.desc()).all()
    return render_template('customer/my_bookings.html', bookings=bookings)

@customer.route('/room-service/<int:booking_id>', methods=['GET', 'POST'])
@customer_required
def room_service(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.customer_id != current_user.id or booking.status != 'active':
        flash('You can only request service for active bookings.', 'danger')
        return redirect(url_for('customer.my_bookings'))
        
    if request.method == 'POST':
        service_type = request.form.get('service_type')
        request_details = request.form.get('request_details')
        
        service_req = ServiceRequest(
            service_type=service_type,
            request_details=request_details,
            booking_id=booking.id,
            hotel_id=booking.hotel_id,
            customer_id=current_user.id
        )
        db.session.add(service_req)
        db.session.commit()
        flash('Service request submitted successfully.', 'success')
        return redirect(url_for('customer.room_service', booking_id=booking.id))
        
    requests = ServiceRequest.query.filter_by(booking_id=booking.id).all()
    return render_template('customer/room_service.html', booking=booking, requests=requests)
