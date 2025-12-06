# app/auth/routes.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from flasgger import swag_from

from app.extensions import db
from app.models import User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.post("/register")
@swag_from({
    "tags": ["Auth"],
    "summary": "Register a new user",
    "description": "Create a new user with username, email, password and optional role.",
    "requestBody": {
        "required": True,
        "content": {
            "application/json": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "username": {"type": "string"},
                        "email": {"type": "string"},
                        "password": {"type": "string"},
                        "role": {"type": "string", "enum": ["admin", "user"]}
                    },
                    "required": ["username", "email", "password"]
                }
            }
        }
    },
    "responses": {
        "201": {
            "description": "User created successfully"
        },
        "400": {
            "description": "User already exists or invalid data"
        }
    }
})
def register():
    """
    Register a new user.
    """
    data = request.get_json() or {}
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    role = data.get("role", "user")

    if not username or not email or not password:
        return jsonify({"message": "username, email and password are required"}), 400

    if role not in ("admin", "user"):
        return jsonify({"message": "role must be 'admin' or 'user'"}), 400

    if User.query.filter((User.username == username) | (User.email == email)).first():
        return jsonify({"message": "User with this username or email already exists"}), 400

    user = User(username=username, email=email, role=role)
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User created successfully", "user": user.to_dict()}), 201


@auth_bp.post("/login")
@swag_from({
    "tags": ["Auth"],
    "summary": "User login",
    "description": "Login with username and password to receive a JWT token.",
    "requestBody": {
        "required": True,
        "content": {
            "application/json": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "username": {"type": "string"},
                        "password": {"type": "string"}
                    },
                    "required": ["username", "password"]
                }
            }
        }
    },
    "responses": {
        "200": {
            "description": "Login successful, returns JWT token"
        },
        "401": {
            "description": "Invalid credentials"
        }
    }
})
def login():
    """
    Login user and return JWT access token.
    """
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"message": "username and password are required"}), 400

    user = User.query.filter_by(username=username).first()

    if not user or not user.check_password(password):
        return jsonify({"message": "Invalid username or password"}), 401

    # Identity can contain user id and role for authorization
    access_token = create_access_token(
        identity={"id": user.id, "role": user.role}
    )

    return jsonify({"access_token": access_token, "user": user.to_dict()}), 200
