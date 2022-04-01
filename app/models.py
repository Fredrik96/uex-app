from flask_login import UserMixin
from datetime import datetime
from app import db, login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def get_user_fitbit_credentials(user_id):
    return FitbitToken.query.filter_by(user_id=user_id).first()

def save_fitbit_token(user_id, access_token, refresh_token):
    fitbit_info = get_user_fitbit_credentials(user_id)
    if not fitbit_info:
        fitbit_info = FitbitToken(None, None, None)
    fitbit_info.user_id = user_id
    fitbit_info.access_token = access_token
    fitbit_info.refresh_token = refresh_token
    db.session.add(fitbit_info)
    db.session.commit()
    return fitbit_info

class UserTable(db.Model):
    __tablename__ = 'datatable'
    id_table = db.Column(db.Integer, primary_key=True)
    users_id = db.Column(db.Integer, db.ForeignKey('userlogs.id'))
    date_time_added = db.Column(db.DateTime, default=datetime.utcnow)
    expname = db.Column(db.String(20))
    tools = db.Column(db.String(40))
    number = db.Column(db.Integer)
    data = db.relationship("UserData", backref=db.backref("data", uselist=False), lazy = 'joined')

class User(UserMixin, db.Model):
    __tablename__ = 'userlogs'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), nullable=False, unique=True)
    email = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(200))
    #backref used to get anything in this class, example: userdata.username
    usertables = db.relationship("UserTable", backref="datatable")

class UserData(db.Model):
    __tablename__ = 'user_data'
    id = db.Column(db.Integer, primary_key=True)
    users_table_id = db.Column(db.Integer, db.ForeignKey('datatable.id_table'))
    video_file = db.Column(db.LargeBinary)
    picture_file = db.Column(db.LargeBinary)
    analytics = db.Column(db.Integer) 
    cardio_file = db.Column(db.Float(4))
    quest_file = db.Column(db.String(200))
    timer = db.Column(db.String(15))
    check = db.Column(db.Integer)

    def __repr__(self):
        return '<timer %r>' % self.timer
    
class FitbitToken(db.Model):
    __tablename__ = 'fitbit_tokens'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('userlogs.id'))
    refresh_token = db.Column(db.String(500))
    access_token = db.Column(db.String(500))

    def __init__(self, user_id, access_token, refresh_token):
        super(FitbitToken, self).__init__()
        self.user_id = user_id
        self.access_token = access_token
        self.refresh_token = refresh_token

    def __repr__(self):
        return '<Token {}, User {}>'.format(self.id, self.user_id)

    def __str__(self):
        return '{} {}'.format(self.id, self.user_id)