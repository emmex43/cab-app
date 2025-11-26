from flask import Flask, render_template, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
import os
from config import Config

db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    app = Flask(__name__, 
                template_folder='../../frontend',
                static_folder='../../frontend')
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    CORS(app)
    
    # Create upload directories
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'vehicles'), exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'documents'), exist_ok=True)
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.rides import rides_bp
    from app.routes.drivers import drivers_bp
    from app.routes.forum import forum_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(rides_bp, url_prefix='/api/rides')
    app.register_blueprint(drivers_bp, url_prefix='/api/drivers')
    app.register_blueprint(forum_bp, url_prefix='/api/forum')
    
    # Serve static files (CSS, JS, images) - FIXED VERSION
    @app.route('/<path:filename>')
    def serve_static(filename):
        # List of static file extensions
        static_extensions = ('.css', '.js', '.jpg', '.jpeg', '.png', '.gif', 
                           '.ico', '.svg', '.ttf', '.woff', '.woff2')
        
        # Check if it's a static file
        if any(filename.endswith(ext) for ext in static_extensions):
            try:
                return send_from_directory(app.static_folder, filename)
            except FileNotFoundError:
                return f"Static file not found: {filename}", 404
        else:
            # If it's not a static file, try to serve as HTML page
            try:
                if filename.endswith('.html'):
                    return render_template(filename)
                else:
                    return render_template(f'{filename}.html')
            except Exception:
                return f"Page not found: {filename}", 404
    
    # Serve frontend pages - FIXED VERSION
    @app.route('/')
    def serve_home():
        return render_template('Home.html')
    
    # This route handles specific pages that don't have extensions
    @app.route('/<page>')
    def serve_pages(page):
        # If it has an extension, it's probably a static file handled above
        if '.' in page and not page.endswith('.html'):
            return serve_static(page)
        
        # Try to render as HTML page
        try:
            if page.endswith('.html'):
                return render_template(page)
            else:
                return render_template(f'{page}.html')
        except Exception:
            return f"Page not found: {page}", 404
    
    return app