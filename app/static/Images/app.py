from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///parkyspot.db'
db = SQLAlchemy(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    bookings = db.relationship('Booking', backref='user', lazy=True)

class ParkingSpot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    rate_per_hour = db.Column(db.Float, nullable=False)
    available = db.Column(db.Boolean, default=True)
    bookings = db.relationship('Booking', backref='parking_spot', lazy=True)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    spot_id = db.Column(db.Integer, db.ForeignKey('parking_spot.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    total_cost = db.Column(db.Float)

# Routes
@app.route('/')
def index():
    return render_template('home.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('signup'))

        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    return render_template('dashboard.html', user=user)


@app.route('/api/parking-spots')
def get_parking_spots():
    lat = float(request.args.get('lat', 0))
    lon = float(request.args.get('lon', 0))
    spots = ParkingSpot.query.filter_by(available=True).all()
    return [{'id': spot.id, 
             'name': spot.name,
             'lat': spot.latitude,
             'lon': spot.longitude,
             'rate': spot.rate_per_hour} for spot in spots]

@app.route('/book/<int:spot_id>', methods=['POST'])
def book_spot(spot_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    spot = ParkingSpot.query.get_or_404(spot_id)
    if not spot.available:
        flash('Spot no longer available')
        return redirect(url_for('home'))

    booking = Booking(
        user_id=session['user_id'],
        spot_id=spot_id,
        start_time=datetime.now(),
        end_time=datetime.now(),  # Update with actual end time
        total_cost=0  # Calculate based on duration and rate
    )
    spot.available = False
    db.session.add(booking)
    db.session.commit()
    return redirect(url_for('bookings'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)