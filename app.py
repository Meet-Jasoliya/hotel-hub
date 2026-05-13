import os
from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager
from models import db, User

def create_app():
    app = Flask(__name__)
    
    # Configuration
    # Use a strong secret key in production
    app.config['SECRET_KEY'] = 'hotel-hub-super-secret-key-2026'
    
    # Configure SQLite database (can be easily swapped to MySQL/PostgreSQL)
    basedir = os.path.abspath(os.path.dirname(__name__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'hotelhub.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize Extensions
    db.init_app(app)
    
    # Setup Flask-Login
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login' # Assuming 'auth.login' is the route for logging in
    login_manager.init_app(app)
    
    # User Loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()
        # Optional: Seed a superadmin if none exists
        # if not User.query.filter_by(role='superadmin').first():
        #     superadmin = User(username='admin', email='admin@hotelhub.com', password_hash='hashed_pw', role='superadmin')
        #     db.session.add(superadmin)
        #     db.session.commit()
            
    # Basic route to verify app is running
    @app.route('/')
    def index():
        from models import Hotel
        # Pass some Indian hotels to the landing page
        hotels = Hotel.query.filter_by(status='approved').limit(3).all()
        return render_template('index.html', hotels=hotels)
        
    @app.route('/about')
    def about():
        return render_template('about.html')
        
    @app.route('/destinations')
    def destinations():
        return render_template('destinations.html')
        
    # Blueprints
    from auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)
    
    from customer import customer as customer_blueprint
    app.register_blueprint(customer_blueprint)
    
    from hoteladmin import hoteladmin as hoteladmin_blueprint
    app.register_blueprint(hoteladmin_blueprint)
    
    from superadmin import superadmin as superadmin_blueprint
    app.register_blueprint(superadmin_blueprint)

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
