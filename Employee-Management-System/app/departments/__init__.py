from flask import Blueprint

departments_bp = Blueprint('departments', __name__)

from app.departments import routes
