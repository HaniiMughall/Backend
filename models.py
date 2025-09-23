from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(180), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    joined = db.Column(db.String(50), default=datetime.utcnow().strftime("%b %Y"))
    points = db.Column(db.Integer, default=0)
    role = db.Column(db.String(20), default="user")  # user | admin
    profile_image = db.Column(db.String(400), nullable=True)
    about = db.Column(db.Text, nullable=True)
    contact = db.Column(db.String(80), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "joined": self.joined,
            "points": self.points,
            "role": self.role,
            "profile_image": self.profile_image,
            "about": self.about,
            "contact": self.contact
        }

class Donor(db.Model):
    __tablename__ = "donors"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    location = db.Column(db.String(200), nullable=True)
    address = db.Column(db.Text, nullable=True)
    phone = db.Column(db.String(80), nullable=True)
    blood_group = db.Column(db.String(6), nullable=False)
    verified = db.Column(db.Boolean, default=False)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "location": self.location,
            "address": self.address,
            "phone": self.phone,
            "blood_group": self.blood_group,
            "verified": self.verified,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "created_at": self.created_at.isoformat()
        }

class BloodRequest(db.Model):
    __tablename__ = "requests"
    id = db.Column(db.Integer, primary_key=True)
    requester_name = db.Column(db.String(120), nullable=True)
    hospital = db.Column(db.String(200), nullable=True)
    city = db.Column(db.String(120), nullable=True)
    blood_group = db.Column(db.String(6), nullable=False)
    phone = db.Column(db.String(80), nullable=True)
    details = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default="pending")  # pending|approved|rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "requester_name": self.requester_name,
            "hospital": self.hospital,
            "city": self.city,
            "blood_group": self.blood_group,
            "phone": self.phone,
            "details": self.details,
            "status": self.status,
            "created_at": self.created_at.isoformat()
        }
