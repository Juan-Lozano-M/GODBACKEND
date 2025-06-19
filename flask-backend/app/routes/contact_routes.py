from flask import Blueprint
from app.controllers.contact_controller import send_contact_email, send_custom_contact_email

# Crear el blueprint para las rutas de contacto
contact_bp = Blueprint('contact', __name__)

@contact_bp.route('/contact/form', methods=['POST'])
def handle_contact_form():
    """
    Ruta para manejar el formulario de contacto por roles
    POST /api/contact/form
    """
    return send_contact_email()

@contact_bp.route('/contact/message', methods=['POST'])
def handle_custom_message():
    """
    Ruta para manejar mensajes de contacto personalizados
    POST /api/contact/message
    """
    return send_custom_contact_email()

@contact_bp.route('/contact/test', methods=['GET'])
def test_contact():
    """
    Ruta de prueba para verificar que el módulo de contacto funciona
    GET /api/contact/test
    """
    return {'message': 'Módulo de contacto funcionando correctamente', 'status': 'ok'}, 200
