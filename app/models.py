# from app import db
# from datetime import datetime



# class SensorData(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     sensor_id = db.Column(db.String(50), nullable=False)  # Changed to String for flexibility
#     status = db.Column(db.String(20), nullable=False)  # "Occupied" or "Available"
#     timestamp = db.Column(db.DateTime, default=datetime.utcnow)
#     parking_spot_id = db.Column(db.Integer, db.ForeignKey('parking_spot.id'), nullable=True)

#     def __repr__(self):
#         return f'<SensorData {self.sensor_id} - {self.status}>'    

# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(80), unique=True, nullable=False)
#     email = db.Column(db.String(120), unique=True, nullable=False)
#     password = db.Column(db.String(128))
#     bookings = db.relationship('Booking', backref='user', lazy=True)
#     parking_spots = db.relationship('ParkingSpot', backref='user', lazy=True)



# class ParkingSpot(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     spot_identifier = db.Column(db.String(10), nullable=False, unique=True)
#     sensor_id = db.Column(db.String(50), nullable=False, unique=True)
#     is_occupied = db.Column(db.Boolean, default=False)
#     last_updated = db.Column(db.DateTime, default=datetime.utcnow)
#     sensor_data = db.relationship('SensorData', backref='parking_spot', lazy=True)
#     bookings = db.relationship('Booking', backref='spot', lazy=True)

# class Booking(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
#     spot_id = db.Column(db.Integer, db.ForeignKey('parking_spot.id'), nullable=False)
#     start_time = db.Column(db.DateTime, nullable=False)
#     end_time = db.Column(db.DateTime, nullable=False)
#     status = db.Column(db.String(20), default='active')  # active, completed, cancelled
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)


# from app import db 
# from datetime import datetime
 

# class SensorData(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     sensor_id = db.Column(db.String(50), nullable=False)
#     status = db.Column(db.String(20), nullable=False)  # "Occupied" or "Available"
#     timestamp = db.Column(db.DateTime, default=datetime.utcnow)
#     parking_spot_id = db.Column(db.Integer, db.ForeignKey('parking_spot.id'), nullable=True)

#     def __repr__(self):
#         return f'<SensorData {self.sensor_id} - {self.status}>'

# class ParkingSpot(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     spot_identifier = db.Column(db.String(10), nullable=False, unique=True)
#     sensor_id = db.Column(db.String(50), nullable=False, unique=True)
#     is_occupied = db.Column(db.Boolean, default=False)
#     last_updated = db.Column(db.DateTime, default=datetime.utcnow)
#     sensor_data = db.relationship('SensorData', backref='parking_spot', lazy=True)
#     bookings = db.relationship('Booking', backref='spot', lazy=True)

# class Booking(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     transaction_id = db.Column(db.String(50), unique=True, nullable=False)
#     spot_id = db.Column(db.Integer, db.ForeignKey('parking_spot.id'), nullable=False)
#     start_time = db.Column(db.DateTime, nullable=False)
#     end_time = db.Column(db.DateTime, nullable=False)
#     status = db.Column(db.String(20), default='active')  # active, completed, cancelled
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)
#     payment_status = db.Column(db.String(20), default='pending')  # pending, completed, failed
    
#     def __repr__(self):
#         return f'<Booking {self.transaction_id}>'





# models.py
from app import db
from datetime import datetime
import qrcode
import io
import base64

class ParkingArea(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    hourly_rate = db.Column(db.Float, nullable=False)
    total_spots = db.Column(db.Integer, nullable=False)
    parking_spots = db.relationship('ParkingSpot', backref='area', lazy=True)
    
    def available_spots_count(self):
        return len([spot for spot in self.parking_spots if not spot.is_occupied])

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'hourly_rate': self.hourly_rate,
            'available_spots': self.available_spots_count(),
            'total_spots': self.total_spots
        }

class SensorData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sensor_id = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    parking_spot_id = db.Column(db.Integer, db.ForeignKey('parking_spot.id'), nullable=True)

    def __repr__(self):
        return f'<SensorData {self.sensor_id} - {self.status}>'

class ParkingSpot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    spot_identifier = db.Column(db.String(10), nullable=False, unique=True)
    sensor_id = db.Column(db.String(50), nullable=False, unique=True)
    is_occupied = db.Column(db.Boolean, default=False)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    area_id = db.Column(db.Integer, db.ForeignKey('parking_area.id'), nullable=False)
    sensor_data = db.relationship('SensorData', backref='parking_spot', lazy=True)
    bookings = db.relationship('Booking', backref='spot', lazy=True)

    def update_status_from_sensor(self, status):
        self.is_occupied = (status == "Occupied")
        self.last_updated = datetime.utcnow()

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.String(50), unique=True, nullable=False)
    spot_id = db.Column(db.Integer, db.ForeignKey('parking_spot.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    payment_status = db.Column(db.String(20), default='pending')
    verification_code = db.Column(db.String(10), unique=True)
    amount = db.Column(db.Float, nullable=False)

    def generate_qr_code(self):
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        data = f"Booking ID: {self.transaction_id}\nSpot: {self.spot.spot_identifier}\nVerification: {self.verification_code}"
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert PIL image to base64
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_str = base64.b64encode(img_buffer.getvalue()).decode()
        return img_str

    def calculate_amount(self):
        duration = (self.end_time - self.start_time).total_seconds() / 3600.0
        return round(duration * self.spot.area.hourly_rate, 2)

    def __repr__(self):
        return f'<Booking {self.transaction_id}>'