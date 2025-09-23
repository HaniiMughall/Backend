# gamification.py
from models import db, User
from sqlalchemy import desc

# Change amounts to whatever makes sense
AWARD_POINTS = {
    
    "DONATE_FORM_SUBMIT": 50,
    
}

def award_points(user_id, action_key):
    pts = AWARD_POINTS.get(action_key, 0)
    if pts == 0:
        return 0
    user = User.query.get(user_id)
    if not user:
        return 0
    user.points = (user.points or 0) + pts
    db.session.commit()
    return pts

def get_leaderboard(limit=10):
    users = User.query.order_by(desc(User.points)).limit(limit).all()
    return [u.to_dict() for u in users]
