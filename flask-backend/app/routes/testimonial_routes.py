# Importación de Blueprint de Flask para crear rutas modulares
from flask import Blueprint

# Importación de los controladores para manejar testimonios
from app.controllers.testimonial_controller import (
    get_testimonials,
    get_testimonials_by_status,
    update_testimonial_status,
    get_testimonial_by_id,
    cambiar_estado_testimonio,
    get_testimonial_stats,
    get_testimonials_with_user,
    create_testimonial,  # Importamos create_testimonial
    delete_testimonial,  # Nueva función para eliminar
    get_testimonials_anulados_antiguos  # Nueva función para obtener antiguos
)

# Creación del Blueprint para las rutas de testimonios
testimonial_bp = Blueprint('testimonial', __name__)

# Rutas para el CRUD de testimonios
testimonial_bp.route('/api/testimonials', methods=['GET'])(get_testimonials)                        # Obtener todos los testimonios
testimonial_bp.route('/api/testimonials/<int:testimonio_id>', methods=['DELETE'])(delete_testimonial) # Eliminar testimonio permanentemente
testimonial_bp.route('/api/testimonials/<int:testimonio_id>/status', methods=['PUT'])(cambiar_estado_testimonio)  # Cambiar estado de un testimonio específico
testimonial_bp.route('/api/testimonials/by-status', methods=['GET'])(get_testimonials_by_status)     # Obtener testimonios por estado
testimonial_bp.route('/api/testimonials/update-status', methods=['PUT'])(update_testimonial_status)  # Actualizar estado del testimonio
testimonial_bp.route('/api/testimonials/id', methods=['GET'])(get_testimonial_by_id)                 # Obtener testimonio por ID
testimonial_bp.route('/api/testimonials/stats', methods=['GET'])(get_testimonial_stats)              # Statísticas de testimonios
testimonial_bp.route('/api/testimonials/with-user', methods=['GET'])(get_testimonials_with_user)     # Obtener testimonios con información del usuario
testimonial_bp.route('/api/testimonials/create', methods=['POST'])(create_testimonial)               # Crear testimonio
testimonial_bp.route('/api/testimonials/anulados-antiguos', methods=['GET'])(get_testimonials_anulados_antiguos) # Obtener testimonios anulados antiguos
