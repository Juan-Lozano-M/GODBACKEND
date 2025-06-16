from flask import jsonify
from app.models.news import News
from app.models.testimonial import Testimonio
from app.models.user import User
from datetime import datetime, timedelta
from sqlalchemy import func
from calendar import month_abbr
from app import db

class StatsController:

    @staticmethod
    def get_general_stats():
        try:
            today = datetime.now().date()
            this_week_start = today - timedelta(days=today.weekday())
            this_month_start = today.replace(day=1)

            total_users = User.query.count()
            total_news = News.query.count()
            total_testimonials = Testimonio.query.count()

            users_this_month = User.query.filter(
                func.date(User.fecha_registro_usu) >= this_month_start
            ).count()

            users_this_week = User.query.filter(
                func.date(User.fecha_registro_usu) >= this_week_start
            ).count()

            users_today = User.query.filter(
                func.date(User.fecha_registro_usu) == today
            ).count()

            active_users_day = 25
            active_users_week = 15
            active_users_month = 10

            traffic_data = [
                {"month": "Ene", "visits": 12000},
                {"month": "Feb", "visits": 14000},
                {"month": "Mar", "visits": 18000},
                {"month": "Abr", "visits": 22000},
                {"month": "May", "visits": 24000},
                {"month": "Jun", "visits": 25000},
                {"month": "Jul", "visits": 24500}
            ]

            visit_stats = {
                "total_visits": 130,
                "home_visits": 45,
                "projects_visits": 35,
                "contact_visits": 25,
                "visit_increase": 55
            }

            return jsonify({
                "success": True,
                "data": {
                    "totals": {
                        "total_registered": total_users,
                        "this_month": users_this_month,
                        "this_week": users_this_week,
                        "today": users_today
                    },
                    "active_users": {
                        "day": active_users_day,
                        "week": active_users_week,
                        "month": active_users_month
                    },
                    "traffic": traffic_data,
                    "visits": visit_stats
                }
            })

        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Error al obtener estadísticas generales: {str(e)}"
            }), 500

    @staticmethod
    def get_news_stats():
        try:
            today = datetime.now().date()
            this_month_start = today.replace(day=1)
            yesterday = today - timedelta(days=1)

            total_news = News.query.count()
            published_today = News.query.filter(
                func.date(News.fecha_creacion) == today
            ).count()

            published_yesterday = News.query.filter(
                func.date(News.fecha_creacion) == yesterday
            ).count()

            created_this_month = News.query.filter(
                func.date(News.fecha_creacion) >= this_month_start
            ).count()

            total_views = db.session.query(func.sum(News.views))\
                .filter(News.es_publicada == 'publicada').scalar() or 0

            total_shares = db.session.query(func.sum(News.shares))\
                .filter(News.es_publicada == 'publicada').scalar() or 0

            most_viewed_news = News.query.filter(News.es_publicada == 'publicada')\
                .order_by(News.views.desc())\
                .limit(3).all()

            most_viewed = [
                {
                    "title": n.titulo_noticia,
                    "category": n.categoria_noticia,
                    "views": n.views,
                    "fecha_creacion": n.fecha_creacion.isoformat() 
                }
                for n in most_viewed_news
            ]

            recent_news_query = News.query.filter(News.es_publicada == 'publicada')\
                .order_by(News.fecha_creacion.desc())\
                .limit(2).all()

            recent_news = [
                {
                    "title": n.titulo_noticia,
                    "category": n.categoria_noticia,
                    "views": n.views,
                    "fecha_creacion": n.fecha_creacion.isoformat() 
                }
                for n in recent_news_query
            ]

            # Consulta de conteo por categoría
            categories_query = db.session.query(
                News.categoria_noticia, func.count(News.id_noticia)
            ).group_by(News.categoria_noticia).all()

            # Lista completa de categorías esperadas
            all_categories = ['deportes', 'tecnologia', 'politica', 'cultura', 'salud', 'economia', 'educacion', 'ciencia']

            # Diccionario con los resultados
            category_counts = {name.lower(): count for name, count in categories_query}

            # Construcción de lista asegurando que todas estén presentes
            categories = [
                {"name": cat.capitalize(), "count": category_counts.get(cat, 0)}
                for cat in all_categories
            ]

            return jsonify({
                "success": True,
                "data": {
                    "totals": {
                        "total_news": total_news,
                        "published_today": published_today,
                        "published_yesterday": published_yesterday,
                        "created_this_month": created_this_month,
                        "total_views": total_views,
                        "total_shares": total_shares
                    },
                    "most_viewed": most_viewed,
                    "recent_news": recent_news,
                    "categories": categories,
                    "category_percentage": 70
                }
            })

        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Error al obtener estadísticas de noticias: {str(e)}"
            }), 500

    @staticmethod
    def get_testimonials_stats():
        try:
            today = datetime.now().date()
            this_month_start = today.replace(day=1)

            total_testimonials = Testimonio.query.count()

            approved = Testimonio.query.filter_by(estado_tes='aprobado').count()
            rejected = Testimonio.query.filter_by(estado_tes='anulado').count()
            pending = Testimonio.query.filter_by(estado_tes='en espera').count()

            monthly_change = Testimonio.query.filter(
                func.date(Testimonio.fecha_publicacion_tes) >= this_month_start
            ).count()

            approved_change = Testimonio.query.filter(
                Testimonio.estado_tes == 'aprobado',
                func.date(Testimonio.fecha_publicacion_tes) >= this_month_start
            ).count()

            rejected_change = Testimonio.query.filter(
                Testimonio.estado_tes == 'anulado',
                func.date(Testimonio.fecha_publicacion_tes) >= this_month_start
            ).count()

            pending_change = Testimonio.query.filter(
                Testimonio.estado_tes == 'en espera',
                func.date(Testimonio.fecha_publicacion_tes) >= this_month_start
            ).count()

            approval_rate = round((approved / total_testimonials * 100), 2) if total_testimonials > 0 else 0
            rejection_rate = round((rejected / total_testimonials * 100), 2) if total_testimonials > 0 else 0
            pending_rate = round((pending / total_testimonials * 100), 2) if total_testimonials > 0 else 0

            meses = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
            current_year = today.year
            trend_dict = {(current_year, i + 1): 0 for i in range(12)}

            monthly_counts = (
                db.session.query(
                    func.extract('year', Testimonio.fecha_publicacion_tes).label('year'),
                    func.extract('month', Testimonio.fecha_publicacion_tes).label('month'),
                    func.count().label('count')
                )
                .filter(
                    Testimonio.fecha_publicacion_tes != None,
                    Testimonio.estado_tes == 'aprobado'  # ← CAMBIO aquí
                )
                .group_by('year', 'month')
                .order_by('year', 'month')
                .all()
            )


            for row in monthly_counts:
                year = int(row.year)
                month = int(row.month)
                if year == current_year:
                    trend_dict[(year, month)] = int(row.count)

            submission_trend = [
                {"month": meses[m - 1], "count": trend_dict[(current_year, m)]}
                for m in range(1, 13)
            ]

            return jsonify({
                "success": True,
                "data": {
                    "totals": {
                        "total_testimonials": total_testimonials,
                        "approved": approved,
                        "rejected": rejected,
                        "pending": pending,
                        "approval_rate": approval_rate,
                        "monthly_change": monthly_change,
                        "approved_change": approved_change,
                        "rejected_change": rejected_change,
                        "pending_change": pending_change
                    },
                    "distribution": {
                        "approved_percentage": approval_rate,
                        "rejected_percentage": rejection_rate,
                        "pending_percentage": pending_rate
                    },
                    "trend": submission_trend
                }
            })

        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Error al obtener estadísticas de testimonios: {str(e)}"
            }), 500
