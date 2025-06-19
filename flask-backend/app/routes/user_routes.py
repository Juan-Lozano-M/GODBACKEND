# Importación de Blueprint de Flask para crear rutas modulares
from flask import Blueprint
# Importación de los controladores para manejar operaciones del usuario
from app.controllers.user_controller import get_user_profile, update_user_profile, update_user_interests, update_user_email, update_user_birthdate, update_user_institution, get_admin_profile

# Creación del Blueprint para las rutas de usuario
user_bp = Blueprint('user', __name__)

# Ruta para obtener el perfil del usuario - Acepta solicitudes GET
user_bp.route('/api/user/profile', methods=['GET'])(get_user_profile)

# Ruta para actualizar el perfil del usuario - Acepta solicitudes PUT
user_bp.route('/api/user/profile', methods=['PUT'])(update_user_profile)

# Ruta para actualizar los intereses del usuario - Acepta solicitudes PUT
user_bp.route('/api/user/interests', methods=['PUT'])(update_user_interests)

user_bp.route('/api/user/email', methods=['PUT', 'OPTIONS'])(update_user_email)

user_bp.route('/api/user/birthdate', methods=['PUT'])(update_user_birthdate)

user_bp.route('/api/user/institution', methods=['PUT'])(update_user_institution)

user_bp.route('/api/user/profile/admin', methods=['GET'])(get_admin_profile)