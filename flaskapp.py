from flask import Flask, render_template, redirect, request, url_for, flash, Response, jsonify
from flask_bootstrap import Bootstrap
from flask_sqlalchemy  import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_migrate import Migrate
from forms import LoginForm, RegisterForm

import cv2
from threading import Thread
from video import record, gen_frames, switch, getCam

app = Flask(__name__)
app.config['SECRET_KEY'] = 'qwertyqwerty'
#SQLite
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
#MYSQL users
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:mypass@localhost/app_users'
#MYSQL userdata
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:mypass@localhost/app_users_data'

bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/features')
def features():
    return render_template('features.html')

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

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/profile', methods=['GET','POST'])
@login_required
def index():
    global mychecks,parttakers
    if request.method == 'POST':
        checks = request.form.getlist('ckbox')
        if checks != [] and int(checks[0]) > 0:
            parttakers = checks.pop(0)
            mychecks = checks
        print(mychecks, flush=True)
        for i in range(len(mychecks)):
            if mychecks[i] == "quest":
                return redirect(url_for('quest'))
            elif mychecks[i] == "vid":
                return redirect(url_for('video'))
            else:
                print("No Tools were chosen!", flush=True)
                break     
    return render_template('profile.html', name=current_user.username)

@app.route('/quest', methods=['GET','POST'])
def quest():
    # if request.method == 'POST':
        # click = request.form['clicks']
        # i = 0
        # if i < int(click):
        #     #print(i, flush=True)
        #     if 'questsub' in request.form:
        #         if not request.form.get('q1'):
        #             flash(u'All Questions must be answered', 'warning')
        #             return redirect(url_for('questionnaire'))

        #         elif not request.form.get('q2'):
        #             flash(u'All Questions must be answered', 'warning')
        #             return redirect(url_for('questionnaire'))

        #         elif not request.form.get('q3'):
        #             flash(u'All Questions must be answered', 'warning')
        #             return redirect(url_for('questionnaire'))
        #         else:
        #             q1=request.form['q1']
        #             q2=request.form['q2']
        #             q3=request.form['q3']
        #             quest.append({'q1': q1, 'q2': q2, 'q3': q3})
        #             print(quest, flush=True)
        # else:
        #     return redirect(url_for('dashboard'))
    return render_template('questionnaire.html')

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


@app.route('/support')
def support():
    return render_template('support.html')


#custom error pages
#invalid url
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

#internal server error
@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html"), 500

@app.route('/video')
def video():
    return render_template('video.html',tools=mychecks)

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/videotasks', methods=['POST','GET'])
def tasks():
    global switch
    if request.method == 'POST':
        print(switch, flush=True)
        if request.form.get('stop') == 'Open/Close':
            if(int(switch)==1):
                switch=0
                getCam(0)
            else:
                getCam(1)
                switch=1
        elif request.form.get('rec') == 'start/stop rec':
            global rec, out
            rec= not rec
            if(rec):
                now=datetime.now() 
                fourcc = cv2.VideoWriter_fourcc(*'XVID')
                out = cv2.VideoWriter('vid_{}.avi'.format(str(now).replace(":",'')), fourcc, 20.0, (640, 480))
                #Start new thread for recording the video
                thread = Thread(target = record, args=[out,])
                thread.start()
            elif(rec==False):
                out.release()
        elif request.form.get('next') == 'Next Page':
            return redirect(url_for('dashboard'))
    elif request.method=='GET':
        return render_template('video.html', tools=mychecks)
    return render_template('video.html', tools=mychecks)

if __name__ == '__main__':
    app.run(debug=True)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), nullable=False, unique=True)
    email = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(200))
    #backref used to get anything in this class, example: userdata.username
    u_data = db.relationship('UserData', backref='userdata', lazy='dynamic')

class UserData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    video_file = db.Column(db.LargeBinary)
    picture_file = db.Column(db.LargeBinary)
    eeg_file = db.Column(db.String(100))
    analytics = db.Column(db.Integer)
    sensor_file = db.Column(db.Float(4))
    date_time_added = db.Column(db.DateTime, default=datetime.utcnow) 
    cardio_file = db.Column(db.Float(4))
    quest_file = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))