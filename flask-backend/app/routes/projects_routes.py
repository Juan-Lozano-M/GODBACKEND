# Importación de Blueprint de Flask para crear rutas modulares
from flask import Blueprint
# Importación de los controladores para manejar proyectos
from app.controllers.projects_controller import (
    create_project,
    get_all_projects,
    get_project_by_id,
    update_project,
    delete_project,
    search_projects
)

# Creación del Blueprint para las rutas de proyectos
projects_bp = Blueprint('projects', __name__)

# Rutas para el CRUD de proyectos
projects_bp.route('/api/projects', methods=['POST'])(create_project)                        # Crear proyecto
projects_bp.route('/api/projects', methods=['GET'])(get_all_projects)                      # Obtener todos los proyectos
projects_bp.route('/api/projects/<int:project_id>', methods=['GET'])(get_project_by_id)    # Obtener proyecto por ID
projects_bp.route('/api/projects/<int:project_id>', methods=['PATCH', 'PUT'])(update_project)  # Actualizar proyecto
projects_bp.route('/api/projects/<int:project_id>', methods=['DELETE'])(delete_project)   # Eliminar proyecto
projects_bp.route('/api/projects/search', methods=['GET'])(search_projects)               # Buscar proyectos
