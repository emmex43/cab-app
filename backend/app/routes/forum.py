from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import ForumPost, Driver, User, Comment

forum_bp = Blueprint('forum', __name__)

@forum_bp.route('/posts', methods=['GET'])
def get_posts():
    try:
        posts = ForumPost.query.order_by(ForumPost.created_at.desc()).all()
        
        posts_data = []
        for post in posts:
            # Get driver and user info
            driver = Driver.query.get(post.driver_id)
            author_name = "Unknown"
            if driver and driver.user:
                author_name = driver.user.fullname
            
            # Get comments for this post
            comments_data = []
            for comment in post.comments:
                comment_user = User.query.get(comment.user_id)
                comments_data.append({
                    'id': comment.id,
                    'content': comment.content,
                    'author_name': comment_user.fullname if comment_user else "Unknown",
                    'author_is_driver': comment_user.is_driver if comment_user else False,
                    'created_at': comment.created_at.isoformat()
                })
            
            post_data = {
                'id': post.id,
                'title': post.title,
                'content': post.content,
                'author_name': author_name,
                'author_is_driver': True,  # Only drivers can create posts
                'created_at': post.created_at.isoformat(),
                'updated_at': post.updated_at.isoformat(),
                'comments': comments_data,
                'can_delete': True  # Frontend will check if current user is author
            }
            posts_data.append(post_data)
        
        return jsonify({'posts': posts_data}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@forum_bp.route('/create', methods=['POST'])
@jwt_required()
def create_post():
    try:
        user_id = int(get_jwt_identity())
        driver = Driver.query.filter_by(user_id=user_id).first()
        
        if not driver:
            return jsonify({'error': 'Only drivers can create posts'}), 403
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        title = data.get('title')
        content = data.get('content')
        
        if not title:
            return jsonify({'error': 'title is required'}), 400
            
        if not content:
            return jsonify({'error': 'content is required'}), 400
        
        title = title.strip()
        content = content.strip()
        
        if len(title) == 0:
            return jsonify({'error': 'title cannot be empty'}), 400
            
        if len(content) == 0:
            return jsonify({'error': 'content cannot be empty'}), 400

        post = ForumPost(
            driver_id=driver.id,
            title=title,
            content=content
        )
        
        db.session.add(post)
        db.session.commit()
        
        return jsonify({
            'message': 'Post created successfully',
            'post': {
                'id': post.id,
                'title': post.title,
                'content': post.content,
                'author_name': driver.user.fullname if driver.user else "Unknown",
                'created_at': post.created_at.isoformat()
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@forum_bp.route('/posts/<int:post_id>', methods=['DELETE'])
@jwt_required()
def delete_post(post_id):
    try:
        user_id = int(get_jwt_identity())
        driver = Driver.query.filter_by(user_id=user_id).first()
        
        if not driver:
            return jsonify({'error': 'Only drivers can delete posts'}), 403
        
        post = ForumPost.query.get(post_id)
        if not post:
            return jsonify({'error': 'Post not found'}), 404
        
        if post.driver_id != driver.id:
            return jsonify({'error': 'You can only delete your own posts'}), 403
        
        db.session.delete(post)
        db.session.commit()
        
        return jsonify({'message': 'Post deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
            return jsonify({'error': 'Comment content is required'}), 400
        
        comment = Comment(
            post_id=post_id,
            user_id=user_id,
            content=content
        )
        
        db.session.add(comment)
        db.session.commit()
        
        return jsonify({
            'message': 'Comment added successfully',
            'comment': {
                'id': comment.id,
                'content': comment.content,
                'author_name': user.fullname,
                'author_is_driver': user.is_driver,
                'created_at': comment.created_at.isoformat()
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@forum_bp.route('/comments/<int:comment_id>', methods=['DELETE'])
@jwt_required()
def delete_comment(comment_id):
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        comment = Comment.query.get(comment_id)
        if not comment:
            return jsonify({'error': 'Comment not found'}), 404
        
        # Users can only delete their own comments
        if comment.user_id != user_id:
            return jsonify({'error': 'You can only delete your own comments'}), 403
        
        db.session.delete(comment)
        db.session.commit()
        
        return jsonify({'message': 'Comment deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500