from flask_login import UserMixin
from datetime import datetime
from app import db, login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class UserTable(db.Model):
    __tablename__ = 'datatable'
    id_table = db.Column(db.Integer, primary_key=True)
    users_id = db.Column(db.Integer, db.ForeignKey('userlogs.id'))
    date_time_added = db.Column(db.DateTime, default=datetime.utcnow)
    expname = db.Column(db.String(20))
    tools = db.Column(db.String(40))
    quests = db.Column(db.String(40))
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
    video_file = db.Column(db.String(50))
    picture_file = db.Column(db.LargeBinary)
    analytics = db.relationship("Gamedata", backref="gameanalytics")
    analyt_file = db.Column(db.String(100)) 
    cardio_file = db.Column(db.Float(4))
    quest_file = db.Column(db.String(200))
    timer = db.Column(db.String(80))
    check = db.Column(db.Integer)

    def __repr__(self):
        return 'timer :{} , quest_file :{} , subject :{} , analytics:{}'.format(self.timer, self.quest_file, self.check, self.analytics)
    
class Gamedata(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    leftclk = db.Column(db.Integer)
    rightclk = db.Column(db.Integer)
    upclk =db.Column(db.Integer)
    spaceclk = db.Column(db.Integer)
    game_data_id = db.Column(db.Integer, db.ForeignKey('user_data.id'))

    def __init__(self, left, right, up, space, game_id):
        self.leftclk = left
        self.rightclk = right
        self.upclk = up
        self.spaceclk = space
        self.game_data_id = game_id

    def __repr__(self):
        return 'Left_Clicks :{} , Right_Clicks:{} , Up_Clicks:{} , Space_Clicks:{}'.format(self.leftclk, self.rightclk, self.upclk, self.spaceclk)

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