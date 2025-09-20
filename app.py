# app.py
import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt_identity
)
from config import Config
from models import db, User, Donation, NeedRequest
from gamification import award_points, get_leaderboard
from utils import ensure_upload_dir, preprocess_image_for_model
import datetime

# Optional: tensorflow (only if you installed it)
try:
    import tensorflow as tf
    TF_AVAILABLE = True
    # load model example: either saved_model or model.h5
    # model = tf.keras.models.load_model("saved_model")
    # replace with your actual model load
    model = None
except Exception:
    TF_AVAILABLE = False
    model = None

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)
jwt = JWTManager(app)

# init db
db.init_app(app)

# ensure upload dir
ensure_upload_dir(app.config["UPLOAD_FOLDER"])

@app.before_first_request
def create_tables():
    db.create_all()

# ------------- Auth -------------
@app.route("/api/auth/signup", methods=["POST"])
def signup():
    data = request.json or {}
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return jsonify({"msg": "Email and password required"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"msg": "Email already exists"}), 400

    user = User(name=name, email=email, password_hash=generate_password_hash(password))
    db.session.add(user)
    db.session.commit()

    access_token = create_access_token(identity=user.id)
    return jsonify({"user": user.to_dict(), "access_token": access_token}), 201

@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.json or {}
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return jsonify({"msg": "Email and password required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"msg": "Invalid credentials"}), 401

    access_token = create_access_token(identity=user.id)
    return jsonify({"user": user.to_dict(), "access_token": access_token}), 200

# ------------- Profile -------------
@app.route("/api/profile", methods=["GET"])
@jwt_required()
def profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "Not found"}), 404
    return jsonify(user.to_dict())

# ------------- Leaderboard -------------
@app.route("/api/leaderboard", methods=["GET"])
def leaderboard():
    data = get_leaderboard(limit=10)
    return jsonify({"leaderboard": data})

# ------------- Predict (fingerprint) -------------
@app.route("/api/predict", methods=["POST"])
@jwt_required()
def predict():
    """
    Accepts 'file' (multipart/form-data) or a base64 in JSON.
    Returns predicted blood group (example).
    """
    user_id = get_jwt_identity()
    if "file" not in request.files:
        return jsonify({"msg": "No file provided"}), 400

    f = request.files["file"]
    if f.filename == "":
        return jsonify({"msg": "Empty filename"}), 400

    # save
    filename = f"{datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}_{f.filename}"
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    f.save(filepath)

    # preprocess
    arr = preprocess_image_for_model(filepath, target_size=(224,224))

    # model inference (replace with your actual model)
    blood_group = None
    if TF_AVAILABLE and model is not None:
        preds = model.predict(arr)
        # map preds to blood groups according to your model's output
        idx = preds.argmax(axis=-1)[0]
        # example mapping (change)
        mapping = {0: "A+", 1: "A-", 2: "B+", 3: "B-", 4: "AB+", 5: "AB-", 6: "O+", 7: "O-"}
        blood_group = mapping.get(int(idx), "Unknown")
    else:
        # mock/dummy result if TF not available
        blood_group = "A+ (mock)"

    # award points for detection
    award_points(user_id, "DETECT_BLOOD")

    return jsonify({"blood_group": blood_group})

# ------------- Donate submit -------------
@app.route("/api/donate", methods=["POST"])
@jwt_required()
def submit_donate():
    user_id = get_jwt_identity()
    data = request.json or {}
    name = data.get("name")
    location = data.get("location")
    blood_group = data.get("blood_group")
    phone = data.get("phone")

    d = Donation(user_id=user_id, name=name, location=location, blood_group=blood_group, phone=phone)
    db.session.add(d)
    db.session.commit()

    # award points
    award_points(user_id, "DONATE_FORM_SUBMIT")
    return jsonify({"msg": "donation saved"}), 201

# ------------- Need request -------------
@app.route("/api/need", methods=["POST"])
@jwt_required()
def submit_need():
    user_id = get_jwt_identity()
    data = request.json or {}
    patient_name = data.get("patient_name")
    hospital = data.get("hospital")
    blood_group = data.get("blood_group")
    phone = data.get("phone")
    details = data.get("details")

    r = NeedRequest(user_id=user_id, patient_name=patient_name, hospital=hospital, blood_group=blood_group, phone=phone, details=details)
    db.session.add(r)
    db.session.commit()

    award_points(user_id, "NEED_BLOOD_REQUEST")
    return jsonify({"msg": "request submitted"}), 201

# ------------- Simple file serve for uploads (optional) -------------
@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

# ------------- Admin: top users (optional) -------------
@app.route("/api/admin/top-users", methods=["GET"])
def admin_top():
    data = get_leaderboard(limit=50)
    return jsonify({"top": data})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
