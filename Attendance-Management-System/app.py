import os
from flask import Flask, render_template, redirect, url_for, session
from config import Config
from models import db
from models.settings import CollegeSettings
from database.db_setup import verify_and_configure_database, init_db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Verify DB connectivity & fallback if needed before SQLAlchemy initialization
    verify_and_configure_database(app)

    # Ensure uploads folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Initialize SQLAlchemy database engine
    db.init_app(app)

    # Register Blueprints
    from routes.auth_routes import auth_bp
    from routes.admin_routes import admin_bp
    from routes.attendance_routes import attendance_bp
    from routes.report_routes import report_bp
    from routes.student_routes import student_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(student_bp)

    # Context Processor: Pass dynamic College Settings to all HTML templates automatically
    @app.context_processor
    def inject_college_settings():
        settings = CollegeSettings.get_settings()
        return dict(
            college_settings=settings,
            current_user_name=session.get('user_name'),
            current_user_role=session.get('user_role'),
            current_user_code=session.get('user_code')
        )

    # Root route redirect
    @app.route('/')
    def index():
        if 'user_id' in session:
            role = session.get('user_role')
            if role == 'student':
                return redirect(url_for('student.dashboard'))
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('auth.login'))

    # Custom 404 handler
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('auth/login.html', error="Page not found"), 404

    return app

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        init_db(app)
    print("Starting Attendance Management System Server on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
