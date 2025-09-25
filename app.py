from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta
from flask_cors import CORS
from models import db, User, BloodRequest
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

CORS(app)
db.init_app(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# Signup
@app.route("/api/auth/signup", methods=["POST"])
def signup():
    data = request.get_json()
    if not data or not data.get("email") or not data.get("password"):
        return jsonify({"msg": "Missing data"}), 400
    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"msg": "User already exists"}), 400
    hashed_password = bcrypt.generate_password_hash(data["password"]).decode("utf-8")
    user = User(name=data["name"], email=data["email"], password=hashed_password)
    db.session.add(user)
    db.session.commit()
    return jsonify({"msg": "User created successfully"}), 201

# Login
@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data or not data.get("email") or not data.get("password"):
        return jsonify({"msg": "Missing data"}), 400
    user = User.query.filter_by(email=data["email"]).first()
    if not user or not bcrypt.check_password_hash(user.password, data["password"]):
        return jsonify({"msg": "Invalid credentials"}), 401
    access_token = create_access_token(identity=str(user.id), expires_delta=timedelta(hours=1))
    return jsonify({
        "access_token": access_token,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "joined": user.joined,
            "points": user.points
        }
    })

# Profile
@app.route("/api/profile", methods=["GET"])
@jwt_required()
def profile():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404
    return jsonify({
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "joined": user.joined,
        "points": user.points
    })

# Blood Request
@app.route("/api/blood/request", methods=["POST"])
@jwt_required()
def blood_request():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    request_entry = BloodRequest(
        user_id=user_id,
        blood_group=data["blood_group"],
        location=data["location"]
    )
    db.session.add(request_entry)
    db.session.commit()
    return jsonify({"msg": "Request created successfully"}), 201

# Init DB
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
