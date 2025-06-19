from app import db

class VisitStats(db.Model):
    __tablename__ = 'visit_stats'

    id = db.Column(db.Integer, primary_key=True)
    home_visits = db.Column(db.Integer, default=0)
    projects_visits = db.Column(db.Integer, default=0)
    contact_visits = db.Column(db.Integer, default=0)
    news_visits = db.Column(db.Integer, default=0)
