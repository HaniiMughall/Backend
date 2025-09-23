import os, datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from config import Config
from models import db, User, Donor, BloodRequest

# Optional: allow server-side TF later. For now, model will live in the app.
try:
    import tensorflow as tf
    TF_AVAILABLE = True
except Exception:
    TF_AVAILABLE = False

app = Flask(__name__)
app.config.from_object(Config)
CORS(app, resources={r"/api/*": {"origins": "*"}})
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

db.init_app(app)
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# Create tables
with app.app_context():
    db.create_all()


# ---------------- AUTH ----------------
@app.route("/api/auth/signup", methods=["POST"])
def signup():
    data = request.get_json() or {}
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return jsonify({"msg": "Email and password required"}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"msg": "Email already exists"}), 400
    pw_hash = bcrypt.generate_password_hash(password).decode("utf-8")
    u = User(name=name or "User", email=email, password_hash=pw_hash)
    db.session.add(u)
    db.session.commit()
    token = create_access_token(identity=str(u.id))
    return jsonify({"user": u.to_dict(), "access_token": token}), 201


@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return jsonify({"msg": "Email and password required"}), 400
    u = User.query.filter_by(email=email).first()
    if not u or not bcrypt.check_password_hash(u.password_hash, password):
        return jsonify({"msg": "Invalid credentials"}), 401
    token = create_access_token(identity=str(u.id))
    return jsonify({"access_token": token, "user": u.to_dict()}), 200


@app.route("/api/profile", methods=["GET"])
@jwt_required()
def profile():
    uid = int(get_jwt_identity())
    u = User.query.get(uid)
    if not u:
        return jsonify({"msg": "User not found"}), 404
    return jsonify(u.to_dict()), 200


@app.route("/api/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    uid = int(get_jwt_identity())
    u = User.query.get(uid)
    if not u:
        return jsonify({"msg": "User not found"}), 404
    data = request.get_json() or {}
    u.name = data.get("name", u.name)
    u.about = data.get("about", u.about)
    u.contact = data.get("contact", u.contact)
    u.profile_image = data.get("profile_image", u.profile_image)
    db.session.commit()
    return jsonify({"msg": "Profile updated", "user": u.to_dict()}), 200


# ---------------- Donors ----------------
@app.route("/api/donors", methods=["POST"])
@jwt_required()
def add_donor():
    data = request.get_json() or {}
    d = Donor(
        name=data.get("name"),
        location=data.get("location"),
        address=data.get("address"),
        phone=data.get("phone"),
        blood_group=data.get("blood_group"),
        verified=bool(data.get("verified", False)),
        latitude=data.get("latitude"),
        longitude=data.get("longitude")
    )
    db.session.add(d)
    db.session.commit()
    return jsonify({"msg": "Donor added", "donor": d.to_dict()}), 201


@app.route("/api/donors", methods=["GET"])
@jwt_required()
def list_donors():
    group = request.args.get("blood_group")
    query = Donor.query
    if group:
        query = query.filter_by(blood_group=group)
    donors = [d.to_dict() for d in query.order_by(Donor.created_at.desc()).all()]
    return jsonify(donors), 200


@app.route("/api/donors/<int:donor_id>", methods=["PUT"])
@jwt_required()
def update_donor(donor_id):
    d = Donor.query.get(donor_id)
    if not d:
        return jsonify({"msg": "Not found"}), 404
    data = request.get_json() or {}
    d.verified = bool(data.get("verified", d.verified))
    db.session.commit()
    return jsonify({"msg": "Updated", "donor": d.to_dict()}), 200


# ---------------- Requests ----------------
@app.route("/api/requests", methods=["POST"])
@jwt_required()
def add_request():
    data = request.get_json() or {}
    r = BloodRequest(
        requester_name=data.get("requester_name"),
        hospital=data.get("hospital"),
        city=data.get("city"),
        blood_group=data.get("blood_group"),
        phone=data.get("phone"),
        details=data.get("details"),
        status=data.get("status", "pending")
    )
    db.session.add(r)
    db.session.commit()
    return jsonify({"msg": "Request created", "request": r.to_dict()}), 201


@app.route("/api/requests", methods=["GET"])
@jwt_required()
def list_requests():
    reqs = [r.to_dict() for r in BloodRequest.query.order_by(BloodRequest.created_at.desc()).all()]
    return jsonify(reqs), 200


@app.route("/api/requests/<int:rid>", methods=["PUT"])
@jwt_required()
def update_request(rid):
    r = BloodRequest.query.get(rid)
    if not r:
        return jsonify({"msg": "Not found"}), 404
    data = request.get_json() or {}
    r.status = data.get("status", r.status)
    db.session.commit()
    return jsonify({"msg": "Updated", "request": r.to_dict()}), 200


# ---------------- History / leaderboard (simple) ----------------
@app.route("/api/history/<int:user_id>", methods=["GET"])
@jwt_required()
def get_history(user_id):
    # very simple: return donors this user submitted and requests they made (extend later)
    donors = [d.to_dict() for d in Donor.query.filter_by().order_by(Donor.created_at.desc()).all()]
    requests = [r.to_dict() for r in BloodRequest.query.filter_by().order_by(BloodRequest.created_at.desc()).all()]
    return jsonify({"donors": donors, "requests": requests}), 200


# ---------------- Serve uploads ----------------
@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


# ---------------- Health ----------------
@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
