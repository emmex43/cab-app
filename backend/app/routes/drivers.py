from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db, socketio
from app.models import Driver, Ride, User

drivers_bp = Blueprint('drivers', __name__)


@drivers_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_driver_profile():
    # ... (Keep existing profile code) ...
    try:
        user_id = int(get_jwt_identity())
        driver = Driver.query.filter_by(user_id=user_id).first()
        if not driver:
            return jsonify({'error': 'Driver profile not found'}), 404

        # ... construct profile_data ...
        profile_data = {
            'driver_id': driver.driver_id,
            'fullname': driver.user.fullname,
        }
        return jsonify({'profile': profile_data}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@drivers_bp.route('/available-rides', methods=['GET'])
@jwt_required()
def get_available_rides():
    return jsonify({'available_rides': []}), 200


@drivers_bp.route('/accept-ride/<int:ride_id>', methods=['POST'])
@jwt_required()
def accept_ride(ride_id):
    try:
        user_id = get_jwt_identity()
        try:
            user_id = int(user_id)
        except:
            pass

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

        #  SIGNAL STUDENT (STABLE VERSION)
        print(f"Emitting acceptance for ride {ride.id}")
        socketio.emit('ride_accepted', {
            'ride_id': ride.id,
            'driver_name': driver.user.fullname,
            'vehicle': driver.vehicle_type,
            'vehicle_id': driver.driver_id,
            'vehicle_desc': driver.vehicle_description
        })

        return jsonify({'message': 'Ride accepted successfully', 'ride': {'id': ride.id}}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
