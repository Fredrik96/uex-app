from flask import Flask
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate

from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
login_manager = LoginManager()

def create_app(config):
    app = Flask(__name__)
    bootstrap = Bootstrap(app)
    migrate = Migrate(app, db)
    app.config.from_object(config)
    config.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    db.app = app

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app