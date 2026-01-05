from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db, socketio
from app.models import Ride, User, Driver
from datetime import datetime, timedelta

rides_bp = Blueprint('rides', __name__)

SHUTTLE_PRICES = {
    'Main Gate/Small Gate': 100,
    'New Benin(NB)': 300,
    'Ring Road(RR)': 300,
    'Back Gate': 100
}


@rides_bp.route('/book', methods=['POST'])
@jwt_required()
def book_ride():
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400

        ride_type = data.get('ride_type')
        destination = data.get('destination')
        pickup_location = data.get('pickup_location', 'UNIBEN Campus')

        if not ride_type:
            return jsonify({'error': 'ride_type is required'}), 400
        if not destination:
            return jsonify({'error': 'destination is required'}), 400

        # --- PRICE & STATUS LOGIC ---
        price = 200          # Default base price
        status = 'pending'   # Default status (waits for driver)

        if ride_type == 'Shuttle':
            price = SHUTTLE_PRICES.get(destination, 200)
            status = 'confirmed'  # Shuttles are auto-confirmed tickets

        elif ride_type == 'Travel':
            # For Travel, we can set a placeholder price or parse it later
            # (Since payment isn't integrated yet, we just record the booking)
            price = 15000 if 'Lagos' in destination else 20000
            status = 'confirmed'  # Travel seats are auto-confirmed

        # Create the Ride Record
        ride = Ride(
            user_id=user_id,
            ride_type=ride_type,
            destination=destination,
            pickup_location=pickup_location,
            price=price,
            status=status
        )

        db.session.add(ride)
        db.session.commit()

        # --- SOCKET ALERT (Only for Cabs) ---
        # We only notify drivers if it is a 'Cab' request.
        # Shuttles and Travel are just ticket bookings.
        if ride_type == 'Cab':
            # Get UTC time now and add 1 hour for Nigeria Time
            nigeria_time = datetime.utcnow() + timedelta(hours=1)
            formatted_time = nigeria_time.strftime("%H:%M")

            student = User.query.get(user_id)

            socketio.emit('new_ride_available', {
                'ride_id': ride.id,
                'student_name': student.fullname,
                'pickup': pickup_location,
                'destination': destination,
                'price': price,
                'type': ride_type,
                'time': formatted_time
            })

        return jsonify({
            'message': f'{ride_type} booked successfully',
            'ride': {
                'id': ride.id,
                'ride_type': ride.ride_type,
                'destination': ride.destination,
                'price': ride.price,
                'status': ride.status,
                'created_at': ride.created_at.isoformat()
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@rides_bp.route('/my-rides', methods=['GET'])
@jwt_required()
def get_my_rides():
    try:
        user_id = int(get_jwt_identity())
        # Sort by newest first
        rides = Ride.query.filter_by(user_id=user_id).order_by(
            Ride.created_at.desc()).all()

        rides_data = []
        for ride in rides:
            driver_name = None
            if ride.assigned_driver and ride.assigned_driver.user:
                driver_name = ride.assigned_driver.user.fullname

            # Convert to Nigeria Time for list display
            local_time = ride.created_at + timedelta(hours=1)

            ride_data = {
                'id': ride.id,
                'ride_type': ride.ride_type,
                'destination': ride.destination,
                'pickup_location': ride.pickup_location,
                'price': ride.price,
                'status': ride.status,
                'created_at': local_time.isoformat(),
                'driver_name': driver_name
            }
            rides_data.append(ride_data)

        return jsonify({'rides': rides_data}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@rides_bp.route('/shuttle-prices', methods=['GET'])
def get_shuttle_prices():
    return jsonify({'prices': SHUTTLE_PRICES}), 200
