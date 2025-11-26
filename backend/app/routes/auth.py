from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app import db
from app.models import User, Driver

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/student/register', methods=['POST'])
def student_register():
    try:
        data = request.get_json()

        # Check if user already exists
        if User.query.filter_by(email=data.get('email')).first():
            return jsonify({'error': 'Email already registered'}), 400

        # Create new user
        user = User(
            fullname=data.get('fullname'),
            email=data.get('email'),
            is_driver=False
        )
        user.set_password(data.get('password'))

        db.session.add(user)
        db.session.commit()

        # FIX: Convert user.id to string for JWT
        access_token = create_access_token(identity=str(user.id))

        return jsonify({
            'message': 'Student registered successfully',
            'access_token': access_token,
            'user': {
                'id': user.id,
                'fullname': user.fullname,
                'email': user.email,
                'is_driver': user.is_driver
            }
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/student/login', methods=['POST'])
def student_login():
    try:
        data = request.get_json()
        user = User.query.filter_by(
            email=data.get('email'), is_driver=False).first()

        if user and user.check_password(data.get('password')):
            # FIX: Convert user.id to string for JWT
            access_token = create_access_token(identity=str(user.id))
            return jsonify({
                'message': 'Login successful',
                'access_token': access_token,
                'user': {
                    'id': user.id,
                    'fullname': user.fullname,
                    'email': user.email,
                    'is_driver': user.is_driver
                }
            }), 200
        else:
            return jsonify({'error': 'Invalid email or password'}), 401

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/driver/register', methods=['POST'])
def driver_register():
    try:
        data = request.form

        # Check if user already exists
        if User.query.filter_by(email=data.get('email')).first():
            return jsonify({'error': 'Email already registered'}), 400

        # Create user account
        user = User(
            fullname=data.get('fullname'),
            email=data.get('email'),
            is_driver=True
        )
        user.set_password(data.get('password'))

        db.session.add(user)
        db.session.flush()  # Get user ID without committing

        # Handle file upload
        vehicle_image = None
        if 'image' in request.files:
            file = request.files['image']
            if file.filename != '':
                filename = f"vehicle_{user.id}_{file.filename}"
                file.save(f'app/static/uploads/vehicles/{filename}')
                vehicle_image = filename

        # Create driver profile
        driver = Driver(
            user_id=user.id,
            driver_id=data.get('id'),
            vehicle_type=data.get('type'),
            vehicle_description=data.get('description'),
            vehicle_image=vehicle_image
        )

        db.session.add(driver)
        db.session.commit()

        # FIX: Convert user.id to string for JWT
        access_token = create_access_token(identity=str(user.id))

        return jsonify({
            'message': 'Driver registered successfully',
            'access_token': access_token,
            'user': {
                'id': user.id,
                'fullname': user.fullname,
                'email': user.email,
                'is_driver': user.is_driver,
                'driver_profile': {
                    'driver_id': driver.driver_id,
                    'vehicle_type': driver.vehicle_type
                }
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/driver/login', methods=['POST'])
def driver_login():
    try:
        data = request.get_json()
        user = User.query.filter_by(
            email=data.get('email'), is_driver=True).first()

        if user and user.check_password(data.get('password')):
            # FIX: Convert user.id to string for JWT
            access_token = create_access_token(identity=str(user.id))
            driver = Driver.query.filter_by(user_id=user.id).first()

            return jsonify({
                'message': 'Login successful',
                'access_token': access_token,
                'user': {
                    'id': user.id,
                    'fullname': user.fullname,
                    'email': user.email,
                    'is_driver': user.is_driver,
                    'driver_profile': {
                        'driver_id': driver.driver_id,
                        'vehicle_type': driver.vehicle_type
                    }
                }
            }), 200
        else:
            return jsonify({'error': 'Invalid email or password'}), 401

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    try:
        # FIX: Convert identity to int for database query
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        user_data = {
            'id': user.id,
            'fullname': user.fullname,
            'email': user.email,
            'is_driver': user.is_driver
        }

        if user.is_driver:
            driver = Driver.query.filter_by(user_id=user.id).first()
            if driver:
                user_data['driver_profile'] = {
                    'driver_id': driver.driver_id,
                    'vehicle_type': driver.vehicle_type,
                    'is_available': driver.is_available
                }

        return jsonify({'user': user_data}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
