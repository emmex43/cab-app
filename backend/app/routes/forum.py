from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db, socketio
from app.models import ForumPost, Driver, User, Comment
from datetime import datetime, timedelta

forum_bp = Blueprint('forum', __name__)

# Helper function to convert UTC to Nigeria Time


def to_nigeria_time(utc_dt):
    if not utc_dt:
        return ""
    # Add 1 hour to UTC time
    nigeria_dt = utc_dt + timedelta(hours=1)
    return nigeria_dt.strftime("%Y-%m-%d %H:%M")

#  GET ALL POSTS


@forum_bp.route('/posts', methods=['GET'])
def get_posts():
    try:
        posts = ForumPost.query.order_by(ForumPost.created_at.desc()).all()

        posts_data = []
        for post in posts:
            driver = Driver.query.get(post.driver_id)
            author_name = "Unknown"
            if driver and driver.user:
                author_name = driver.user.fullname

            comments_data = []
            for comment in post.comments:
                comment_user = User.query.get(comment.user_id)
                comments_data.append({
                    'id': comment.id,
                    'content': comment.content,
                    'author_name': comment_user.fullname if comment_user else "Unknown",
                    'author_is_driver': comment_user.is_driver if comment_user else False,
                    #  USE HELPER
                    'created_at': to_nigeria_time(comment.created_at)
                })

            post_data = {
                'id': post.id,
                'title': post.title,
                'content': post.content,
                'author_name': author_name,
                'author_is_driver': True,
                # <--- USE HELPER
                'created_at': to_nigeria_time(post.created_at),
                'comments': comments_data,
                'can_delete': True
            }
            posts_data.append(post_data)

        return jsonify({'posts': posts_data}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

#  CREATE POST


@forum_bp.route('/create', methods=['POST'])
@jwt_required()
def create_post():
    try:
        user_id = int(get_jwt_identity())
        driver = Driver.query.filter_by(user_id=user_id).first()

        if not driver:
            return jsonify({'error': 'Only drivers can create posts'}), 403

        data = request.get_json()
        title = data.get('title', '').strip()
        content = data.get('content', '').strip()

        if not title or not content:
            return jsonify({'error': 'Title and content are required'}), 400

        post = ForumPost(
            driver_id=driver.id,
            title=title,
            content=content
        )

        db.session.add(post)
        db.session.commit()

        # Broadcast new post
        socketio.emit('new_forum_post', {
            'id': post.id,
            'title': post.title,
            'content': post.content,
            'author_name': driver.user.fullname,
            'created_at': to_nigeria_time(post.created_at),  # <--- USE HELPER
            'comments': []
        })

        return jsonify({'message': 'Post created successfully'}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

#  DELETE POST


@forum_bp.route('/posts/<int:post_id>', methods=['DELETE'])
@jwt_required()
def delete_post(post_id):
    try:
        user_id = int(get_jwt_identity())
        driver = Driver.query.filter_by(user_id=user_id).first()

        if not driver:
            return jsonify({'error': 'Only drivers can delete'}), 403

        post = ForumPost.query.get(post_id)
        if not post:
            return jsonify({'error': 'Post not found'}), 404
        if post.driver_id != driver.id:
            return jsonify({'error': 'Not your post'}), 403

        post_id_copy = post.id
        db.session.delete(post)
        db.session.commit()

        socketio.emit('delete_forum_post', {'id': post_id_copy})

        return jsonify({'message': 'Post deleted successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ADD COMMENT


@forum_bp.route('/posts/<int:post_id>/comments', methods=['POST'])
@jwt_required()
def add_comment(post_id):
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        post = ForumPost.query.get(post_id)
        if not post:
            return jsonify({'error': 'Post not found'}), 404

        data = request.get_json()
        content = data.get('content', '').strip()
        if not content:
            return jsonify({'error': 'Content required'}), 400

        comment = Comment(post_id=post_id, user_id=user_id, content=content)

        db.session.add(comment)
        db.session.commit()

        # Broadcast Comment
        socketio.emit('new_forum_comment', {
            'post_id': post_id,
            'id': comment.id,
            'content': comment.content,
            'author_name': user.fullname,
            #  USE HELPER
            'created_at': to_nigeria_time(comment.created_at)
        })

        return jsonify({'message': 'Comment added'}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# DELETE COMMENT


@forum_bp.route('/comments/<int:comment_id>', methods=['DELETE'])
@jwt_required()
def delete_comment(comment_id):
    try:
        user_id = int(get_jwt_identity())
        comment = Comment.query.get(comment_id)

        if not comment:
            return jsonify({'error': 'Comment not found'}), 404
        if comment.user_id != user_id:
            return jsonify({'error': 'Not your comment'}), 403

        db.session.delete(comment)
        db.session.commit()

        return jsonify({'message': 'Comment deleted'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
