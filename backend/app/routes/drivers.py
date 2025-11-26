from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Driver, Ride, User

drivers_bp = Blueprint('drivers', __name__)


@drivers_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_driver_profile():
    try:
        user_id = int(get_jwt_identity())  # Convert string back to int
        driver = Driver.query.filter_by(user_id=user_id).first()

        if not driver:
            return jsonify({'error': 'Driver profile not found'}), 404

        profile_data = {
            'driver_id': driver.driver_id,
            'fullname': driver.user.fullname,
            'email': driver.user.email,
            'vehicle_type': driver.vehicle_type,
            'vehicle_description': driver.vehicle_description,
            'vehicle_image': driver.vehicle_image,
            'is_available': driver.is_available,
            'license_verified': driver.license_verified
        }

        return jsonify({'profile': profile_data}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@drivers_bp.route('/available-rides', methods=['GET'])
@jwt_required()
def get_available_rides():
    try:
        user_id = int(get_jwt_identity())  # Convert string back to int
        driver = Driver.query.filter_by(user_id=user_id).first()

        if not driver:
            return jsonify({'error': 'Driver not found'}), 404

        available_rides = Ride.query.filter_by(
            ride_type=driver.vehicle_type,
            status='pending'
        ).all()

        rides_data = []
        for ride in available_rides:
            ride_data = {
                'id': ride.id,
                'passenger_name': ride.passenger.fullname,
                'destination': ride.destination,
                'pickup_location': ride.pickup_location,
                'price': ride.price,
                'created_at': ride.created_at.isoformat()
            }
            rides_data.append(ride_data)

        return jsonify({'available_rides': rides_data}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@drivers_bp.route('/accept-ride/<int:ride_id>', methods=['POST'])
@jwt_required()
def accept_ride(ride_id):
    try:
        user_id = get_jwt_identity()
        driver = Driver.query.filter_by(user_id=user_id).first()

        if not driver:
            return jsonify({'error': 'Driver not found'}), 404

        ride = Ride.query.get(ride_id)
        if not ride:
            return jsonify({'error': 'Ride not found'}), 404

        if ride.status != 'pending':
            return jsonify({'error': 'Ride is not available'}), 400

        ride.driver_id = driver.id
        ride.status = 'accepted'

        db.session.commit()

        return jsonify({
            'message': 'Ride accepted successfully',
            'ride': {
                'id': ride.id,
                'passenger_name': ride.passenger.fullname,
                'destination': ride.destination
            }
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@drivers_bp.route('/my-accepted-rides', methods=['GET'])
@jwt_required()
def get_my_accepted_rides():
    try:
        user_id = get_jwt_identity()
        driver = Driver.query.filter_by(user_id=user_id).first()

        if not driver:
            return jsonify({'error': 'Driver not found'}), 404

        accepted_rides = Ride.query.filter_by(
            driver_id=driver.id,
            status='accepted'
        ).all()

        rides_data = []
        for ride in accepted_rides:
            ride_data = {
                'id': ride.id,
                'passenger_name': ride.passenger.fullname,
                'destination': ride.destination,
                'pickup_location': ride.pickup_location,
                'price': ride.price,
                'created_at': ride.created_at.isoformat()
            }
            rides_data.append(ride_data)

        return jsonify({'accepted_rides': rides_data}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
