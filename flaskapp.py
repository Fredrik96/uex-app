from flask import Flask, render_template, redirect, request, url_for, flash, Response, jsonify
from flask_bootstrap import Bootstrap
from flask_sqlalchemy  import SQLAlchemy
from datetime import datetime
from numpy import number
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_migrate import Migrate
from forms import DashboardForm, LoginForm, RegisterForm

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

#routes sorted by when they are rendered

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/features')
def features():
    return render_template('features.html')

@app.route('/support')
def support():
    return render_template('support.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect(url_for('profile'))
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

@app.route('/profile', methods=['GET','POST'])
@login_required
def profile():
    global mychecks
    mychecks = DashboardForm()

    if request.method == 'POST':
        u_id = current_user.id
        checks = request.form.getlist('ckbox')
        mychecks.number = int(checks.pop(0))
        mychecks.expname = checks.pop()

        print(mychecks.tools,flush=True)
        if checks != [] and mychecks.number > 0:
            mychecks.tools = ','.join(checks)
            new_exp = UserTable(users_id=u_id, expname=mychecks.expname, tools=str(mychecks.tools), number=mychecks.number)
            #sql command to execute for reseting the primary key id for UserTable after a row is deleted
            sql = "ALTER TABLE datatable AUTO_INCREMENT = 1"
            db.engine.execute(sql)
            db.session.add(new_exp)
            db.session.commit()
            new_exp_id = new_exp.id_table
            return redirect(url_for('exp_handler', parttakers=mychecks.number, tools=mychecks.tools, new_exp_id=new_exp_id))
        else:
            flash(u'You need to specify at least 1 tool and include 1 participant', 'info')
            return redirect(url_for('profile'))

    return render_template('profile.html', name=current_user.username)

@app.route('/experiments/<int:new_exp_id>', methods=['POST','GET'])
@login_required
def exp_handler(new_exp_id):
    global mychecks
    data_to_exp = UserTable.query.get_or_404(new_exp_id)
    try:
        mychecks
    except NameError:
        mychecks = None

    if mychecks == None:
        mychecks = data_to_exp
    
    if request.method == 'POST':
        start_exp = request.form.get('startexp')
        stop_exp = request.form.get('stopexp')

        if start_exp == "Start Experiment":
            mychecks.number -= 1
            exp_list = data_to_exp.tools.split(',')
            print(exp_list, flush=True)

            if "video" or "analyt" or "time" or "cardio" in exp_list:
                return redirect(url_for('video', new_exp_id=data_to_exp.id_table))

            if "quest" in exp_list:
                return redirect(url_for('quest', new_exp_id=data_to_exp.id_table))

        if stop_exp == "Finnished!":
            return redirect(url_for('dashboard'))

    return render_template('experiments.html', parttakers=mychecks.number, tools=data_to_exp.tools, new_exp_id=data_to_exp.id_table)

@app.route('/quest/<int:new_exp_id>', methods=['GET','POST'])
@login_required
def quest(new_exp_id):
    questions = []
    data_to_quest = UserTable.query.get_or_404(new_exp_id)
    numb = data_to_quest.number

    if request.method == 'POST':
        if 'questsub' in request.form:
            if not request.form.get('q1'):
                flash(u'All Questions must be answered', 'warning')
            elif not request.form.get('q2'):
                flash(u'All Questions must be answered', 'warning')
            elif not request.form.get('q3'):
                flash(u'All Questions must be answered', 'warning')
            else:
                q1=request.form['q1']
                q2=request.form['q2']
                q3=request.form['q3']
                questions.append({q1,q2,q3})
                print(questions, flush=True)
                return redirect(url_for('exp_handler', parttakers=numb, new_exp_id=data_to_quest.id_table))

    return render_template('questionnaire.html', new_exp_id=data_to_quest.id_table)

@app.route('/video/<int:new_exp_id>')
@login_required
def video(new_exp_id):
    data_to_video = UserTable.query.get_or_404(new_exp_id)
    howMany = []
    numb = data_to_video.number
    tools = data_to_video.tools.split(',')
    for i in range(numb):
        howMany.append(i+1)
    return render_template('tasks.html',tools=tools,
                                        new_exp_id=data_to_video.id_table,
                                        howMany = howMany)

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/tasks/<int:new_exp_id>', methods=['POST','GET'])
@login_required
def tasks(new_exp_id):
    #declare some variables to avoid undefined when reloading page
    global switch
    data_to_tasks = UserTable.query.get_or_404(new_exp_id)
    howMany = []
    numb = data_to_tasks.number
    tools = data_to_tasks.tools.split(',')
    mysession = None
    exp_session = ''
    exp_session_first = ''
    for i in range(numb):
        howMany.append(i+1)

    if request.method == 'POST':
        #getting the session data in order to change the html according to who is in session
        exp_session = request.form.getlist('session')
        done_session = request.form.get('donesess')
        print(done_session,flush=True)
        
        if exp_session == []:
            exp_session = "in Progress"

        exp_session = ' '.join(exp_session)
        print(exp_session,flush=True)
        exp_session_first = exp_session[-1]
        
        if exp_session == []:
            exp_session = "Progress"

        if done_session != None:
            exp_session_first = done_session[-1]
        else:
            done_session = "None"

        if "Session" in exp_session:
            mysession = "In Session " + exp_session_first
        elif "Done" in done_session:
            mysession = "Done " + exp_session_first
        print(mysession,flush=True)

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

        if request.form.get('startanlytic') != None:
            flash(u'Analytics started', 'info')
        elif request.form.get('startcardio') != None:
            flash(u'Cardio started', 'info')
        elif request.form.get('starttimer') != None:
            flash(u'Timer started', 'info')
        elif request.form.get('next') == 'Next Page':
            if "quest" in data_to_tasks.tools:
                return redirect(url_for('quest', new_exp_id=data_to_tasks.id_table))
            else:
                return redirect(url_for('exp_handler', parttakers=numb, new_exp_id=data_to_tasks.id_table))

    return render_template('tasks.html', tools=tools,
                                         new_exp_id=data_to_tasks.id_table,
                                         howMany = howMany,
                                         mysession = mysession,
                                         exp_session = exp_session_first)

@app.route('/dashboard')
@login_required
def dashboard():
    current_u_id = current_user.id
    my_exp = UserTable.query.order_by(UserTable.id_table) 

    return render_template('dashboard.html', my_exp=my_exp, current_u_id=current_u_id)

@app.route('/delete/<int:id>')
def delete(id):
    current_u_id = current_user.id
    data_to_delete = UserTable.query.get_or_404(id)
    try:
        db.session.delete(data_to_delete)
        db.session.commit()
        print("Data Deleted Successfully!",id, flush=True)
        my_exp = UserTable.query.order_by(UserTable.id_table)
        return render_template('dashboard.html', my_exp=my_exp, current_u_id=current_u_id)
    except:
        print("Not Able To Delete Data", flush=True)
        return render_template('dashboard.html', my_exp=my_exp, current_u_id=current_u_id)

@app.route('/add/<int:id>', methods=['GET', 'POST'])
def add(id):
    data_to_add = UserTable.query.get_or_404(id)
    current_numb = data_to_add.number
    if request.method == 'POST':
        mychecks.new_number = request.form.get('addnew')
        updated_numb = current_numb + int(mychecks.new_number)
        update_db = UserTable(number=updated_numb)
        db.session.add(update_db)
        db.session.commit()
        print(updated_numb, flush=True)
    return render_template('experiments.html', parttakers=mychecks.new_number)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

#custom error pages
#invalid url
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

#internal server error
@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html"), 500

if __name__ == '__main__':
    app.run(debug=True)

class UserTable(db.Model):
    __tablename__ = 'datatable'
    id_table = db.Column(db.Integer, primary_key=True)
    users_id = db.Column(db.Integer, db.ForeignKey('userlogs.id'))
    users_data_id = db.Column(db.Integer, db.ForeignKey('user_data.id'))
    date_time_added = db.Column(db.DateTime, default=datetime.utcnow)
    expname = db.Column(db.String(20))
    tools = db.Column(db.String(40))
    number = db.Column(db.Integer)
    userdata = db.relationship("UserData", backref="user_data")
    user = db.relationship("User", backref="userlogs")

class User(UserMixin, db.Model):
    __tablename__ = 'userlogs'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), nullable=False, unique=True)
    email = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(200))
    #backref used to get anything in this class, example: userdata.username
    user_data = db.relationship('UserTable', back_populates='user', lazy='dynamic')

class UserData(db.Model):
    __tablename__ = 'user_data'
    id = db.Column(db.Integer, primary_key=True)
    video_file = db.Column(db.LargeBinary)
    picture_file = db.Column(db.LargeBinary)
    analytics = db.Column(db.Integer) 
    cardio_file = db.Column(db.Float(4))
    quest_file = db.Column(db.String(200))
    users = db.relationship('UserTable', back_populates='userdata', lazy='dynamic')