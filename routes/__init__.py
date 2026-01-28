from flask import Blueprint

# Import blueprints
from .auth import auth_bp
from .user import user_bp
from .admin import admin_bp

def register_blueprints(app):
    """Register all blueprints with the Flask app"""
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(admin_bp)
