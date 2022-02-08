from cv2 import VideoCapture
from flask import Flask, render_template, redirect, request, url_for, flash, Response
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import InputRequired, Email, Length
from flask_sqlalchemy  import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import cv2
from threading import Thread

from video import gen_frames, switch, rec, out, record, camera


app = Flask(__name__)
app.config['SECRET_KEY'] = 'qwertyqwerty'
#SQLite
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
#MYSQL users
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:mypass@localhost/app_users'
#MYSQL userdata
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:mypass@localhost/app_users_data'

bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class UserData(db.Model):
    parttaker_id = db.Column(db.Integer, primary_key=True)
    video_file = db.Column(db.LargeBinary)
    picture_file = db.Column(db.LargeBinary)
    eeg_file = db.Column(db.String(100))
    analytics = db.Column(db.Integer)
    sensor_file = db.Column(db.Float(4))
    date_time_added = db.Column(db.DateTime, default=datetime.utcnow) 
    cardio_file = db.Column(db.Float(4))
    quest_file = db.Column(db.String(200))
    

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), nullable=False, unique=True)
    email = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(200))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('remember me')
    login = SubmitField(label='Login')


class RegisterForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect(url_for('index'))
        flash(u'Username or password is incorect', 'error')
    return render_template('login.html', form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        users = User.query.filter_by(username=form.username.data).first()
        mymails = User.query.filter_by(email=form.email.data).first()
        if users or mymails:
            #db.session.query(User).delete()
            #db.session.commit()
            flash(u'User or email is taken', 'error')
            return redirect(url_for('signup'))

        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        form.username.data=''
        form.email.data=''
        flash(u'User added successfully!', 'success')
    my_users = User.query.order_by(User.id)
    return render_template('signup.html', form=form, my_users=my_users)


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/features')
def features():
    return render_template('features.html')

@app.route('/support')
def support():
    return render_template('support.html')

@app.route('/home')
@login_required
def index():
    return render_template('profile.html', name=current_user.username)

@app.route('/dashboard')
def dashboard():
    camera.release()
    cv2.destroyAllWindows()
    return render_template('dashboard.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)

#----------------------------
# @app.route('/video')
# def video():
#     return render_template('video.html')

# @app.route('/video_feed')
# def video_feed():
#     return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# @app.route('/tasks', methods=['POST','GET'])
# def tasks():
#     global switch, camera
#     if request.method == 'POST':
#         if request.form.get('start') == 'startstop':
#             if(switch==True):
#                 switch=False
#                 camera.release()
#                 cv2.destroyAllWindows()
#             else:
#                 camera = cv2.VideoCapture(0)
#                 switch=True
#         elif request.form.get('rec') == 'startstoprec':
#             global rec, out
#             rec= not rec
#             if(rec):
#                 now=datetime.now() 
#                 fourcc = cv2.VideoWriter_fourcc(*'XVID')
#                 out = cv2.VideoWriter('vid_{}.avi'.format(str(now).replace(":",'')), fourcc, 20.0, (640, 480))
#                 #Start new thread for recording the video
#                 thread = Thread(target = record, args=[out,])
#                 thread.start()
#             elif(rec==False):
#                 out.release()
#     elif request.method=='GET':
#         return render_template('video.html')
#     return render_template('video.html')
#-------------------------

