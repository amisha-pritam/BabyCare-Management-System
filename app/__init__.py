from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = "babycare_secret_key"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///babycare.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = "main.login"

    from . import models

    from .routes import main
    app.register_blueprint(main)

    return app