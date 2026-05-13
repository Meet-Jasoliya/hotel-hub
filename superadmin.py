from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, User, Hotel, Booking
from functools import wraps

superadmin = Blueprint('superadmin', __name__, url_prefix='/superadmin')

def superadmin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'superadmin':
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@superadmin.route('/dashboard')
@superadmin_required
def dashboard():
    pending_hotels = Hotel.query.filter_by(status='pending').count()
    total_users = User.query.count()
    approved_hotels = Hotel.query.filter_by(status='approved').count()
    
    return render_template('superadmin/dashboard.html', 
                           pending_hotels=pending_hotels,
                           total_users=total_users,
                           approved_hotels=approved_hotels)

@superadmin.route('/pending-hotels')
@superadmin_required
def pending_hotels():
    hotels = Hotel.query.filter_by(status='pending').all()
    return render_template('superadmin/pending_hotels.html', hotels=hotels)

@superadmin.route('/approve-hotel/<int:hotel_id>')
@superadmin_required
def approve_hotel(hotel_id):
    hotel = Hotel.query.get_or_404(hotel_id)
    hotel.status = 'approved'
    db.session.commit()
    flash(f'Hotel "{hotel.name}" has been approved.', 'success')
    return redirect(url_for('superadmin.pending_hotels'))

@superadmin.route('/reject-hotel/<int:hotel_id>')
@superadmin_required
def reject_hotel(hotel_id):
    hotel = Hotel.query.get_or_404(hotel_id)
    hotel.status = 'rejected'
    db.session.commit()
    flash(f'Hotel "{hotel.name}" has been rejected.', 'warning')
    return redirect(url_for('superadmin.pending_hotels'))

@superadmin.route('/users')
@superadmin_required
def all_users():
    users = User.query.all()
    return render_template('superadmin/users.html', users=users)

@superadmin.route('/bookings')
@superadmin_required
def all_bookings():
    bookings = Booking.query.order_by(Booking.id.desc()).all()
    return render_template('superadmin/all_bookings.html', bookings=bookings)

@superadmin.route('/generate-bill/<int:booking_id>')
@superadmin_required
def generate_bill(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    from datetime import date
    return render_template('hoteladmin/bill.html', booking=booking, current_date=date.today().strftime('%B %d, %Y'))
