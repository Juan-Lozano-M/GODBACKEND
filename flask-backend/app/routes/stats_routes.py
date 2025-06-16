from flask import Blueprint
from app.controllers.stats_controller import StatsController

# Crear el blueprint para las rutas de estadísticas
stats_bp = Blueprint('stats', __name__)

@stats_bp.route('/api/stats/general', methods=['GET'])
def get_general_stats():
    return StatsController.get_general_stats()

@stats_bp.route('/api/stats/news', methods=['GET'])
def get_news_stats():
    return StatsController.get_news_stats()

@stats_bp.route('/api/stats/testimonials', methods=['GET'])
def get_testimonials_stats():
    return StatsController.get_testimonials_stats()

@stats_bp.route('/api/stats/dashboard', methods=['GET'])
def get_dashboard_stats():
    try:
        general_stats_response = StatsController.get_general_stats()
        news_stats_response = StatsController.get_news_stats()
        testimonials_stats_response = StatsController.get_testimonials_stats()

        if isinstance(general_stats_response, tuple):
            general_stats_response = general_stats_response[0]
        if isinstance(news_stats_response, tuple):
            news_stats_response = news_stats_response[0]
        if isinstance(testimonials_stats_response, tuple):
            testimonials_stats_response = testimonials_stats_response[0]

        general_stats = general_stats_response.get_json()
        news_stats = news_stats_response.get_json()
        testimonials_stats = testimonials_stats_response.get_json()

        # 🔍 Imprimir para debug
        print("🧪 general_stats:", general_stats)
        print("🧪 news_stats:", news_stats)
        print("🧪 testimonials_stats:", testimonials_stats)

        return {
            "success": True,
            "data": {
                "general": general_stats.get("data") if general_stats.get("success") else {},
                "news": news_stats.get("data") if news_stats.get("success") else {},
                "testimonials": testimonials_stats.get("data") if testimonials_stats.get("success") else {}
            }
        }
    except Exception as e:
        print("🔥 Error en get_dashboard_stats:", str(e))
        return {
            "success": False,
            "message": f"Error al obtener estadísticas del dashboard: {str(e)}"
        }, 500
