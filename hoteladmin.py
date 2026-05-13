import os
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from models import db, Hotel, Room, Booking, ServiceRequest
from functools import wraps

hoteladmin = Blueprint('hoteladmin', __name__, url_prefix='/hoteladmin')

def hoteladmin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'hoteladmin':
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@hoteladmin.route('/dashboard', methods=['GET', 'POST'])
@hoteladmin_required
def dashboard():
    # Check if the admin has a hotel, if not they can create one
    hotel = Hotel.query.filter_by(owner_id=current_user.id).first()
    
    if request.method == 'POST' and not hotel:
        name = request.form.get('name')
        description = request.form.get('description')
        address = request.form.get('address')
        
        image_path = None
        if 'hotel_image' in request.files:
            file = request.files['hotel_image']
            if file and file.filename != '':
                filename = secure_filename(f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}")
                upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'hotel_images')
                os.makedirs(upload_dir, exist_ok=True)
                file.save(os.path.join(upload_dir, filename))
                image_path = f"uploads/hotel_images/{filename}"
        
        new_hotel = Hotel(name=name, description=description, address=address, owner_id=current_user.id, image_path=image_path)
        db.session.add(new_hotel)
        db.session.commit()
        flash('Hotel registration submitted and is pending Super Admin approval.', 'success')
        return redirect(url_for('hoteladmin.dashboard'))
        
    return render_template('hoteladmin/dashboard.html', hotel=hotel)

@hoteladmin.route('/rooms', methods=['GET', 'POST'])
@hoteladmin_required
def manage_rooms():
    hotel = Hotel.query.filter_by(owner_id=current_user.id).first()
    if not hotel or hotel.status != 'approved':
        flash('Your hotel is not approved yet or you have not registered one.', 'warning')
        return redirect(url_for('hoteladmin.dashboard'))
        
    if request.method == 'POST':
        room_number = request.form.get('room_number')
        room_type = request.form.get('room_type')
        price = request.form.get('price_per_night')
        
        new_room = Room(room_number=room_number, room_type=room_type, price_per_night=float(price), hotel_id=hotel.id)
        db.session.add(new_room)
        db.session.commit()
        flash('Room added successfully.', 'success')
        return redirect(url_for('hoteladmin.manage_rooms'))
        
    rooms = Room.query.filter_by(hotel_id=hotel.id).all()
    return render_template('hoteladmin/manage_rooms.html', rooms=rooms, hotel=hotel)

@hoteladmin.route('/bookings')
@hoteladmin_required
def bookings():
    hotel = Hotel.query.filter_by(owner_id=current_user.id).first()
    if not hotel:
        return redirect(url_for('hoteladmin.dashboard'))
        
    all_bookings = Booking.query.filter_by(hotel_id=hotel.id).all()
    return render_template('hoteladmin/bookings.html', bookings=all_bookings, hotel=hotel)

@hoteladmin.route('/service-requests', methods=['GET', 'POST'])
@hoteladmin_required
def service_requests():
    hotel = Hotel.query.filter_by(owner_id=current_user.id).first()
    if not hotel:
        return redirect(url_for('hoteladmin.dashboard'))
        
    requests = ServiceRequest.query.filter_by(hotel_id=hotel.id).order_by(ServiceRequest.created_at.desc()).all()
    return render_template('hoteladmin/service_requests.html', requests=requests, hotel=hotel)

@hoteladmin.route('/update-request/<int:request_id>/<status>')
@hoteladmin_required
def update_request(request_id, status):
    req = ServiceRequest.query.get_or_404(request_id)
    # Ensure this request belongs to a hotel owned by current admin
    if req.hotel.owner_id == current_user.id:
        if status in ['in_progress', 'completed']:
            req.status = status
            db.session.commit()
            flash('Service request status updated.', 'success')
    return redirect(url_for('hoteladmin.service_requests'))

@hoteladmin.route('/accept-booking/<int:booking_id>')
@hoteladmin_required
def accept_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.hotel.owner_id == current_user.id and booking.status == 'pending':
        booking.status = 'active'
        db.session.commit()
        flash('Booking accepted successfully.', 'success')
    return redirect(url_for('hoteladmin.bookings'))

@hoteladmin.route('/reject-booking/<int:booking_id>')
@hoteladmin_required
def reject_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.hotel.owner_id == current_user.id and booking.status == 'pending':
        booking.status = 'rejected'
        booking.room.is_available = True
        db.session.commit()
        flash('Booking rejected.', 'warning')
    return redirect(url_for('hoteladmin.bookings'))

@hoteladmin.route('/generate-bill/<int:booking_id>')
@hoteladmin_required
def generate_bill(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.hotel.owner_id != current_user.id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('hoteladmin.bookings'))
    from datetime import date
    return render_template('hoteladmin/bill.html', booking=booking, current_date=date.today().strftime('%B %d, %Y'))
