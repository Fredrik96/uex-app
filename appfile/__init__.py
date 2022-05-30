from flask import Flask
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate
from flask_moment import Moment

from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData

convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

db = SQLAlchemy(metadata=metadata)
login_manager = LoginManager()

def create_app(config):
    app = Flask(__name__)
    bootstrap = Bootstrap(app)
    migrate = Migrate(app, db)
    moment = Moment(app)
    #app.config.from_object(config)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://pkkfxybimfvdff:26cbe64d988bc53e68f254d61689ca142401bc867d2446c25c69ab33eec79c4f@ec2-44-194-117-205.compute-1.amazonaws.com:5432/d6gujdtsf5l8ce'
    config.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    db.app = app

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app