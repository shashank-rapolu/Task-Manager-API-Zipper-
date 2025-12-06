# app/__init__.py
from flask import Flask
from flasgger import Swagger

from app.config import Config
from app.extensions import db, bcrypt, jwt
from app.auth.routes import auth_bp
from app.tasks.routes import tasks_bp


def create_app(testing: bool = False) -> Flask:
    """
    Application factory function. Pass testing=True in tests
    to use an in-memory SQLite DB.
    """
    app = Flask(__name__)
    app.config.from_object(Config)

    if testing:
        app.config["TESTING"] = True
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(tasks_bp)

    # Initialize Swagger for API docs (available at /apidocs)
    Swagger(app)

    # Simple health check
    @app.get("/health")
    def health_check():
        return {"status": "ok"}, 200

    return app