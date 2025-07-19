from flask import render_template, request, redirect, url_for, flash, session, jsonify
from sqlalchemy import func
from app import app, db, socketio
from app.models import SensorData, db, ParkingSpot, Booking, ParkingArea
from datetime import datetime




@app.route('/')
def home():
    # Get all parking areas with their spots and sensor data
    parking_areas = ParkingArea.query.all()
    areas_data = []

    for area in parking_areas:
        spots_data = []
        available_count = 0
        
        for spot in area.parking_spots:
            # Get latest sensor data
            latest_sensor = SensorData.query.filter_by(
                sensor_id=spot.sensor_id
            ).order_by(SensorData.timestamp.desc()).first()
            
            is_available = latest_sensor.status == 'Available' if latest_sensor else True
            if is_available:
                available_count += 1
            
            spots_data.append({
                'id': spot.id,
                'spot_identifier': spot.spot_identifier,
                'is_available': is_available
            })

        areas_data.append({
            'id': area.id,
            'name': area.name,
            'latitude': area.latitude,
            'longitude': area.longitude,
            'hourly_rate': area.hourly_rate,
            'total_spots': len(spots_data),
            'available_spots': available_count,
            'spots': spots_data
        })

    return render_template('home.html', parking_areas=areas_data)

@app.route('/api/parking-areas')
def get_parking_areas():
    lat = float(request.args.get('lat', 0))
    lon = float(request.args.get('lon', 0))
    
    # Get all parking areas
    parking_areas = ParkingArea.query.all()
    areas_data = []

    for area in parking_areas:
        # Calculate distance (simplified)
        distance = ((area.latitude - lat) ** 2 + (area.longitude - lon) ** 2) ** 0.5
        
        if distance <= 5:  # Within 5 units
            spots_data = []
            available_count = 0
            
            for spot in area.parking_spots:
                latest_sensor = SensorData.query.filter_by(
                    sensor_id=spot.sensor_id
                ).order_by(SensorData.timestamp.desc()).first()
                
                is_available = latest_sensor.status == 'Available' if latest_sensor else True
                if is_available:
                    available_count += 1
                
                spots_data.append({
                    'id': spot.id,
                    'spot_identifier': spot.spot_identifier,
                    'is_available': is_available
                })

            areas_data.append({
                'id': area.id,
                'name': area.name,
                'latitude': area.latitude,
                'longitude': area.longitude,
                'hourly_rate': area.hourly_rate,
                'total_spots': len(spots_data),
                'available_spots': available_count,
                'spots': spots_data,
                'distance': distance
            })

    return jsonify(areas_data)










@app.route('/sensordata')
def sensor():
    """Display sensor data from the database."""
    
    return render_template('sensor_data.html')

@app.route('/update-sensor-data', methods=['POST'])
def update_sensor_data():
    """Receive sensor data from ESP32 and broadcast it via WebSocket."""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Process and store data
        sensor_status = []
        for sensor, status in data.items():
            sensor_id = int(sensor.replace("sensor", ""))
            status_text = "Available" if status else "Occupied"

            # Save to database
            new_data = SensorData(sensor_id=sensor_id, status=status_text)
            db.session.add(new_data)
            sensor_status.append({"sensor_id": sensor_id, "status": status_text})

        db.session.commit()

        # Emit real-time update to WebSocket clients
        socketio.emit('sensor_update', sensor_status)

        return jsonify({"message": "Data updated successfully"}), 200
    except Exception as e:
        print(f"Error in update_sensor_data: {str(e)}")
        return jsonify({"error": str(e)}), 500
    


@app.route('/add-parking-area', methods=['GET', 'POST'])
def add_parking_area():
    if request.method == 'POST':
        try:
            new_area = ParkingArea(
                name=request.form['name'],
                latitude=float(request.form['latitude']),
                longitude=float(request.form['longitude']),
                hourly_rate=float(request.form['hourly_rate']),
                total_spots=int(request.form['total_spots'])
            )
            db.session.add(new_area)
            db.session.commit()
            flash('Parking area added successfully', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            flash(f'Error adding parking area: {str(e)}', 'error')
            db.session.rollback()
            return render_template('add_parking_area.html')
    # GET request
    return render_template('add_parking_area.html')




@app.route('/add-parking-spot', methods=['GET', 'POST'])
def add_parking_spot():
    if request.method == 'POST':
        try:
            # Create new parking spot
            new_spot = ParkingSpot(
                spot_identifier=request.form['spot_identifier'],
                sensor_id=request.form['sensor_id'],
                area_id=int(request.form['area_id']),
                latitude=float(request.form['latitude']),
                longitude=float(request.form['longitude']),
                is_occupied=False
            )
            print("New spot object:",new_spot)
            db.session.add(new_spot)
            db.session.commit()
            
            flash('Parking spot added successfully', 'success')
            return redirect(url_for('index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding parking spot: {str(e)}', 'error')
            parking_areas = ParkingArea.query.all()
            return render_template('add_parking_spot.html', parking_areas=parking_areas)
    
    # GET request - show form
    parking_areas = ParkingArea.query.all()
    return render_template('add_parking_spot.html', parking_areas=parking_areas)

@app.route('/api/parking-area/<int:area_id>')
def get_parking_area(area_id):
    try:
        area = ParkingArea.query.get_or_404(area_id)
        return jsonify({
            'id': area.id,
            'name': area.name,
            'latitude': area.latitude,
            'longitude': area.longitude,
            'total_spots': area.total_spots,
            'available_spots': area.available_spots_count()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/parking-spots/<int:area_id>')
def get_area_spots(area_id):
    try:
        spots = ParkingSpot.query.filter_by(area_id=area_id).all()
        return jsonify([{
            'id': spot.id,
            'identifier': spot.spot_identifier,
            'is_occupied': spot.is_occupied,
            'latitude': spot.latitude,
            'longitude': spot.longitude
        } for spot in spots])
    except Exception as e:
        return jsonify({'error': str(e)}), 500








