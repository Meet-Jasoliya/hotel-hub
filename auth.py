from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect_based_on_role(current_user.role)

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Logged in successfully.', 'success')
            return redirect_based_on_role(user.role)
        else:
            flash('Please check your login details and try again.', 'danger')
            
    return render_template('auth/login.html')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect_based_on_role(current_user.role)

    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role') # 'customer' or 'hoteladmin'
        
        # Superadmin cannot be registered via public form
        if role not in ['customer', 'hoteladmin']:
            role = 'customer'

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email address already exists.', 'warning')
            return redirect(url_for('auth.register'))

        new_user = User(
            email=email, 
            username=username, 
            password_hash=generate_password_hash(password, method='scrypt'),
            role=role
        )

        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@auth.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        current_user.username = request.form.get('username')
        current_user.email = request.form.get('email')
        
        new_password = request.form.get('new_password')
        if new_password:
            current_user.password_hash = generate_password_hash(new_password, method='scrypt')
            
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('auth.profile'))
        
    return render_template('auth/profile.html')

@auth.route('/profile/delete', methods=['POST'])
@login_required
def delete_account():
    user = User.query.get(current_user.id)
    # Logging out before deleting the record
    logout_user()
    db.session.delete(user)
    db.session.commit()
    flash('Your account and all associated data have been deleted.', 'info')
    return redirect(url_for('index'))

def redirect_based_on_role(role):
    if role == 'superadmin':
        return redirect(url_for('superadmin.dashboard'))
    elif role == 'hoteladmin':
        return redirect(url_for('hoteladmin.dashboard'))
    else:
        return redirect(url_for('customer.dashboard'))
