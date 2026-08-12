from flask import Blueprint

employees_bp = Blueprint('employees', __name__)

from app.employees import routes
