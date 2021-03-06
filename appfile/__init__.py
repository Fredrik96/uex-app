from flask import Flask
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate
from flask_moment import Moment
from flask_socketio import SocketIO

from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
import os

from video import Camera
from process import webopencv
import logging
from sys import stdout

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

camera = Camera(webopencv())

def create_app(config):
    app = Flask(__name__)
    bootstrap = Bootstrap(app)
    migrate = Migrate(app, db)
    moment = Moment(app)
    #app.config.from_object(config)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://pkkfxybimfvdff:26cbe64d988bc53e68f254d61689ca142401bc867d2446c25c69ab33eec79c4f@ec2-44-194-117-205.compute-1.amazonaws.com:5432/d6gujdtsf5l8ce'
    SECRET_KEY = os.urandom(32)
    app.config['SECRET_KEY'] = SECRET_KEY
    app.logger.addHandler(logging.StreamHandler(stdout))
    app.config['DEBUG'] = True
    socketio = SocketIO(app, logger=True)
    config.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    db.app = app
    

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    @socketio.on('input image', namespace='/test')
    def test_message(input):
        input = input.split(",")[1]
        camera.enqueue_input(input)

    @socketio.on('connect', namespace='/test')
    def test_connect():
        app.logger.info("client connected")

    return app, socketio
    
def gen():
    while True:
        frame = camera.get_frame() 
        yield (b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
