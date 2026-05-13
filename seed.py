from app import create_app
from models import db, User, Hotel, Room
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    # Clear existing data
    db.drop_all()
    db.create_all()

    # Create Superadmin
    superadmin = User(
        username="Super Admin",
        email="admin@hotelhub.com",
        password_hash=generate_password_hash("admin123", method="scrypt"),
        role="superadmin"
    )
    db.session.add(superadmin)

    # Create Hotel Admins
    hotel_admin1 = User(
        username="Taj Admin",
        email="taj@hotelhub.com",
        password_hash=generate_password_hash("hotel123", method="scrypt"),
        role="hoteladmin"
    )
    hotel_admin2 = User(
        username="Leela Admin",
        email="leela@hotelhub.com",
        password_hash=generate_password_hash("hotel123", method="scrypt"),
        role="hoteladmin"
    )
    db.session.add_all([hotel_admin1, hotel_admin2])
    db.session.commit()

    # Create Hotels
    hotel1 = Hotel(
        name="The Taj Mahal Palace",
        description="Built in 1903, the iconic Taj Mahal Palace stands majestically opposite the Gateway of India, overlooking the Arabian Sea. Experience legendary Indian hospitality.",
        address="Apollo Bunder, Colaba, Mumbai",
        status="approved",
        owner_id=hotel_admin1.id
    )
    hotel2 = Hotel(
        name="The Leela Palace",
        description="Experience the grandeur of Rajasthan's royal heritage. Located on the serene banks of Lake Pichola, offering spectacular views of the Aravalli mountains.",
        address="Lake Pichola, Udaipur, Rajasthan",
        status="approved",
        owner_id=hotel_admin2.id
    )
    hotel3 = Hotel(
        name="Taj Exotica Resort & Spa",
        description="A Mediterranean-style 5-star resort stretching over 56 acres of lush gardens along Benaulim Beach. Perfect for a tropical Goan retreat.",
        address="Benaulim, Goa",
        status="approved",
        owner_id=hotel_admin1.id
    )
    db.session.add_all([hotel1, hotel2, hotel3])
    db.session.commit()

    # Create Rooms
    rooms = [
        Room(room_number="101", room_type="Luxury City View", price_per_night=18000.0, hotel_id=hotel1.id),
        Room(room_number="102", room_type="Taj Club Sea View", price_per_night=35000.0, hotel_id=hotel1.id),
        
        Room(room_number="201", room_type="Heritage Lake View", price_per_night=42000.0, hotel_id=hotel2.id),
        Room(room_number="202", room_type="Maharaja Suite", price_per_night=125000.0, hotel_id=hotel2.id),
        
        Room(room_number="301", room_type="Garden Villa", price_per_night=22000.0, hotel_id=hotel3.id),
    ]
    db.session.bulk_save_objects(rooms)

    # Create Customer
    customer = User(
        username="Jane Smith",
        email="customer@example.com",
        password_hash=generate_password_hash("guest123", method="scrypt"),
        role="customer"
    )
    db.session.add(customer)
    db.session.commit()

    print("Database seeded with Indian Luxury Hotels successfully!")
