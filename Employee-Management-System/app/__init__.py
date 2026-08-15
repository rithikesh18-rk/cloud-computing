import os
from flask import Flask, render_template
from app.config import Config, get_db_uri
from app.extensions import db, login_manager

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.config['SQLALCHEMY_DATABASE_URI'] = get_db_uri()

    # Ensure Flask instance directory and upload folders exist
    os.makedirs(app.instance_path, exist_ok=True)
    instance_path = os.path.join(app.root_path, '..', 'instance')
    upload_path = os.path.join(app.root_path, 'static', 'uploads', 'profile_pics')
    os.makedirs(instance_path, exist_ok=True)
    os.makedirs(upload_path, exist_ok=True)


    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)

    # Register Blueprints
    from app.auth import auth_bp
    from app.employees import employees_bp
    from app.dashboard import dashboard_bp
    from app.departments import departments_bp
    from app.attendance import attendance_bp
    from app.leave import leave_bp
    from app.profile import profile_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(employees_bp, url_prefix='/employees')
    app.register_blueprint(dashboard_bp, url_prefix='/')
    app.register_blueprint(departments_bp, url_prefix='/departments')
    app.register_blueprint(attendance_bp, url_prefix='/attendance')
    app.register_blueprint(leave_bp, url_prefix='/leave')
    app.register_blueprint(profile_bp, url_prefix='/profile')

    # Global Error Handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500



    # Initialize database tables and seed default admin account inside app context
    with app.app_context():
        from app.models import init_database
        init_database()

    return app

