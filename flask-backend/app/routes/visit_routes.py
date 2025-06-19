from flask import Blueprint
from app.controllers.visit_controller import register_visit

visit_routes = Blueprint('visit_routes', __name__)

# Ruta POST para registrar visitas
visit_routes.route('/api/stats/register-visit', methods=['POST'])(register_visit)
