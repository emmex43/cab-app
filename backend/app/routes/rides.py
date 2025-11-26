from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Ride, User, Driver

rides_bp = Blueprint('rides', __name__)

# Price mapping based on your frontend
SHUTTLE_PRICES = {
    'Main Gate/Small Gate': 200,
    'New Benin(NB)': 300,
    'Ring Road(RR)': 300,
    'Back Gate': 200
}

@rides_bp.route('/book', methods=['POST'])
@jwt_required()
def book_ride():
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        # Check if data is None (no JSON sent)
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        ride_type = data.get('ride_type')  # 'Cab' or 'Shuttle'
        destination = data.get('destination')
        pickup_location = data.get('pickup_location', 'UNIBEN Campus')
        
        # Validate required fields
        if not ride_type:
            return jsonify({'error': 'ride_type is required'}), 400
            
        if not destination:
            return jsonify({'error': 'destination is required'}), 400
        
        # Calculate price
        if ride_type == 'Shuttle':
            price = SHUTTLE_PRICES.get(destination, 200)
        else:
            price = 200  # Default cab price
        
        # Create ride
        ride = Ride(
            user_id=user_id,
            ride_type=ride_type,
            destination=destination,
            pickup_location=pickup_location,
            price=price,
            status='pending'
        )
        
        db.session.add(ride)
        db.session.commit()
        
        return jsonify({
            'message': 'Ride booked successfully',
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
        rides = Ride.query.filter_by(user_id=user_id).order_by(Ride.created_at.desc()).all()
        
        rides_data = []
        for ride in rides:
            driver_name = None
            if ride.assigned_driver and ride.assigned_driver.user:
                driver_name = ride.assigned_driver.user.fullname
                
            ride_data = {
                'id': ride.id,
                'ride_type': ride.ride_type,
                'destination': ride.destination,
                'pickup_location': ride.pickup_location,
                'price': ride.price,
                'status': ride.status,
                'created_at': ride.created_at.isoformat(),
                'driver_name': driver_name
            }
            rides_data.append(ride_data)
        
        return jsonify({'rides': rides_data}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@rides_bp.route('/shuttle-prices', methods=['GET'])
def get_shuttle_prices():
    return jsonify({'prices': SHUTTLE_PRICES}), 200