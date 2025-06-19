from flask import request, jsonify
from app import db
from app.models.visit_stats import VisitStats

def register_visit():
    try:
        data = request.get_json()
        section = data.get('section')

        if section not in ['home', 'projects', 'contact', 'news']:
            return jsonify({
                "status": "error",
                "message": "Sección inválida. Usa: 'home', 'projects' o 'contact' o 'news'."
            }), 400

        stats = VisitStats.query.get(1)
        if not stats:
            return jsonify({
                "status": "error",
                "message": "Registro de visitas no inicializado."
            }), 404

        if section == 'home':
            stats.home_visits += 1
        elif section == 'projects':
            stats.projects_visits += 1
        elif section == 'contact':
            stats.contact_visits += 1
        elif section == 'news':
            stats.news_visits += 1

        db.session.commit()

        return jsonify({
            "status": "success",
            "message": f"Visita registrada en la sección: {section}"
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": f"Error al registrar visita: {str(e)}"
        }), 500
