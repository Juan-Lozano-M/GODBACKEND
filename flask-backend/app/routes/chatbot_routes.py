from flask import Blueprint
from app.controllers.chatbot_controller import send_message, get_predefined_responses

# Crear el Blueprint para las rutas del chatbot
chatbot_bp = Blueprint('chatbot', __name__)

# Ruta para enviar mensajes al chatbot (sin el prefijo completo)
chatbot_bp.route('/message', methods=['POST'])(send_message)

# Ruta para obtener respuestas predefinidas (sin el prefijo completo)
chatbot_bp.route('/predefined', methods=['GET'])(get_predefined_responses)