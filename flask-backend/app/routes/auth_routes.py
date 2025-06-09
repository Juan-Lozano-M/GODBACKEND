from flask import Blueprint
from app.controllers.auth_controller import register_user, login_user, request_password_reset, update_email

auth_bp = Blueprint('auth', __name__)

auth_bp.route('/register', methods=['POST'])(register_user)
auth_bp.route('/login', methods=['POST'])(login_user)
auth_bp.route('/request-reset', methods=['POST'])(request_password_reset)
auth_bp.route('/update-email', methods=['POST'])(update_email)