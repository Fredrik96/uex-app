from flask import flash, jsonify, url_for, redirect, render_template, request, Response
from flask_login import logout_user, login_required, login_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os

from appfile import db
from forms import RegisterForm, LoginForm, DashboardForm
from appfile.models import User, UserTable, UserData, Gamedata
from . import main

import cv2
from camera import VideoCamera
from video import Camera

from process import webopencv 

video_camera = None
global_frame = None

camera = Camera(webopencv())

def gen():
    """Video streaming generator function."""
    while True:
        frame = camera.get_frame() 
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@main.route('/vidfeed')
def vidfeed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')


@main.route('/')
def index():
    return render_template('index.html')

@main.route('/about')
def about():
    return render_template('about.html')

@main.route('/features')
def features():
    return render_template('features.html')

@main.route('/support')
def support():
    return render_template('support.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect(url_for('main.profile'))
        flash(u'Username or password is incorect', 'error')
    return render_template('login.html', form=form)

@main.route('/signup', methods=['GET', 'POST'])
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

@main.route('/profile', methods=['GET','POST'])
def profile():
    global mychecks
    mychecks = DashboardForm()
    number = '0'
    if not current_user.is_authenticated:
        return redirect(url_for('main.login'))

    u_id = current_user.id
    if request.method == 'POST':
        checks = request.form.getlist('ckbox')
        print(checks,flush=True)
        mychecks.expname = checks.pop(0)
        mychecks.number = int(checks.pop(0))
        mychecks.quests = sorted([i for i in checks if i[0].isupper()])
        mychecks.tools = sorted([i for i in checks if i[0].islower()])
        print(mychecks.quests,flush=True)
        if checks != [] and mychecks.number > 0:
            mychecks.quests = ','.join(mychecks.quests)
            mychecks.tools = ','.join(mychecks.tools)
            new_exp = UserTable(users_id=u_id, expname=mychecks.expname, tools=str(mychecks.tools), quests=str(mychecks.quests), number=mychecks.number)
            db.session.add(new_exp)
            db.session.expire_on_commit=False
            db.session.commit()
            new_exp_id = new_exp.id_table
            return redirect(url_for('main.tasks', number=number, numb=mychecks.number, tools=mychecks.tools, new_exp_id=new_exp_id, quests=mychecks.quests))
        else:
            flash(u'You need to specify at least 1 tool and include 1 participant', 'info')
            return redirect(url_for('main.profile'))

    return render_template('profile.html', name=current_user.username)

@main.route('/quest/<int:new_exp_id>', methods=['GET','POST'])
@login_required
def quest(new_exp_id):
    current_u_id = current_user.id
    data_to_quest = UserTable.query.get_or_404(new_exp_id)
    scales = ''

    if request.method == 'POST':
        questionnaires = request.form.getlist("questscale")
        scales = ','.join(questionnaires)
        new_data = UserData(quest_file=scales, users_table_id=data_to_quest.id_table)
        db.session.add(new_data)
        db.session.commit()

        my_exp = UserTable.query.order_by(UserTable.id_table)
        return render_template('dashboard.html', current_u_id=current_u_id, my_exp=my_exp, my_quest=questionnaires)
    return render_template('questionnaire.html', new_exp_id=data_to_quest.id_table,
                                                 new_exp_name=data_to_quest.expname)

# @main.route('/table_row_push', methods=['GET'])
# def push_table_data():
#     row = request.args.get('startanalytics')
#     if request.method == 'GET':
#         print(row, flush=True)
#         return jsonify([row])
#     return jsonify([row])

@main.route('/gamelist_add/<int:new_exp_id>', methods=['POST'])
def gamelist_add(new_exp_id):
    data_to_game = UserTable.query.get_or_404(new_exp_id)
    table_id = data_to_game.id_table
    data = request.get_json()
    print(data, flush=True)
    new_left = data['left']
    new_right = data['right']
    new_up = data['up']
    new_space = data['space']
    gamer_user = Gamedata(left=new_left, right=new_right, up=new_up, space=new_space, game_id=table_id)
    db.session.add(gamer_user)
    db.session.commit()
    # db.session.query(Gamedata).delete()
    # db.session.commit()
    print("Successfully added!",gamer_user.id, flush=True)
    return "OK"

@main.route('/record_status/<int:number>/<int:row>', methods=['POST'])
@login_required
def record_status(number,row):
    global video_camera
    if video_camera == None:
        video_camera = VideoCamera(number,row)

    json = request.get_json()
    status = json['status']

    if status == "true":
        if video_camera == None:
            video_camera.start_cam()
        print("recording", flush=True)
        video_camera.start_record(number,row)
        return jsonify(result="started")
    else:
        video_camera.stop_record()
        print(video_camera.is_open,flush=True)
        return jsonify(result="stopped")

def video_stream(number,row):
    global video_camera 
    global global_frame
    
    if video_camera == None:
        video_camera = VideoCamera(number,row)
        
    while True:
        frame = video_camera.get_frame()
        if video_camera.is_open == False:
            break
        if frame != None:
            global_frame = frame
            yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        else:
            yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + global_frame + b'\r\n\r\n')
    cv2.destroyAllWindows()
    video_camera.is_open = True
        

@main.route('/video_viewer/<int:number>/<int:row>')
def video_viewer(number,row):
    return Response(video_stream(number,row), mimetype='multipart/x-mixed-replace; boundary=frame')

@main.route('/tasks/<int:new_exp_id>/<int:number>', methods=['POST','GET'])
@login_required
def tasks(new_exp_id,number):
    #declare some variables to avoid undefined when reloading page
    data_to_tasks = UserTable.query.get_or_404(new_exp_id)
    my_exp_game = Gamedata.query.filter_by(game_data_id= new_exp_id)
    new_exp_name = data_to_tasks.expname
    quests = data_to_tasks.quests
    data_number = []
    analytics = []
    howMany = []
    progress = 0
    numb = data_to_tasks.number
    tools = data_to_tasks.tools

    for gamedata in my_exp_game:
        analytics.append(gamedata)

    if data_to_tasks.data != []:
        for elem in data_to_tasks.data:
            data_number.append(elem.check)

    progress = len(data_to_tasks.data)

    for i in range(numb):
        howMany.append(i+1)

    my_exp = UserTable.query.order_by(UserTable.id_table)

    try:
        number #this number is the number of the participant who is in session
    except:
        pass

    if request.method == 'POST':
        session_check = request.args.get("number")
        if(number != None):
            session_check = number
            
        if request.form.get('savesession') != None:
            timer = request.form.getlist('savesession')
            print(timer, flush=True)
            for item in timer:
                if item != "Init":
                    timer = item
            print(timer, flush=True)   
            new_data = UserData(timer=str(timer), quest_file=quests, video_file=data_to_tasks.expname, users_table_id=data_to_tasks.id_table, check=session_check)
            db.session.add(new_data)
            db.session.commit()
            timer = ""
            print("New data commited to UserData", flush=True)

        if request.form.get('next') == 'To Dashboard':
            current_u_id = current_user.id
            return redirect(url_for('main.dashboard', my_exp=my_exp, current_u_id=current_u_id))
        if request.form.get('sessiontest') != None:
            return redirect(url_for('main.experiments', new_exp_name=new_exp_name, numb=numb, new_exp_id=new_exp_id, number=number))
    return render_template('tasks.html', tools=tools, new_exp_name=new_exp_name,
                                         new_exp_id=data_to_tasks.id_table,
                                         howMany = howMany,
                                         number=number,
                                         numb=numb,
                                         quests=quests,
                                         data_to_tasks=data_to_tasks,
                                         data_number=data_number,
                                         progress=progress)

@main.route('/process/timer/<int:new_exp_id>', methods=['GET'])
def process_timer(new_exp_id):
    data_table = UserTable.query.get_or_404(new_exp_id)
    howMany = []
    numb = data_table.number
    tools = data_table.tools.split(',')
    for i in range(numb):
        howMany.append(i+1)

    if request.method == 'GET':
        timer = request.args.get('timerInput')
        if(timer!=""):    
            new_data = UserData(timer=timer, users_table_id=data_table.id_table)
            db.session.add(new_data)
            db.session.commit()
            print("Timer commited to UserData", flush=True)
    return render_template('tasks.html',tools=tools,
                                        new_exp_id=data_table.id_table,
                                        howMany = howMany,numb = numb)

@main.route('/process/<int:new_exp_id>', methods=['POST','GET'])
def process(new_exp_id):

    if request.method == 'POST':
        in_session = request.form.get('session')

        if in_session != None:
            return jsonify({'in_session' : in_session})
        else:
            print("Not retreived done",flush=True)

@main.route('/process/done', methods=['POST'])
def process_done():
    done_session = request.form.get('donesess')
    if done_session != None:
        print(done_session, flush=True)
        return jsonify({'done_session' : done_session})
    else:
        print("Not retreived done")


@main.route('/dashboard')
@login_required
def dashboard():
    current_u_id = current_user.id
    my_exp = UserTable.query.order_by(UserTable.id_table)
    for exp in my_exp:
        print(exp.users_id, flush=True)

    return render_template('dashboard.html', my_exp=my_exp, current_u_id=current_u_id)

@main.route('/delete/<int:id>')
@login_required
def delete(id):
    current_u_id = current_user.id
    row_to_delete = UserTable.query.get_or_404(id)
    try:
        db.session.delete(row_to_delete)
        db.session.commit()
        print("Data Deleted Successfully!",id, flush=True)
        my_exp = UserTable.query.order_by(UserTable.id_table)
        return render_template('dashboard.html', my_exp=my_exp, current_u_id=current_u_id)
    except:
        print("Not Able To Delete Data", flush=True)
        my_exp = UserTable.query.order_by(UserTable.id_table)
        return render_template('dashboard.html', my_exp=my_exp, current_u_id=current_u_id)

@main.route('/add/<int:id>', methods=['GET', 'POST'])
@login_required
def add(id):
    data_to_add = UserTable.query.get_or_404(id)
    my_exp_game = Gamedata.query.filter_by(game_data_id= id)
    current_numb = data_to_add.number
    tools = data_to_add.tools
    new_exp_name = data_to_add.expname
    quests = data_to_add.quests
    howMany = []
    data_number = []
    analytics = []
    progress = 0
    updated_numb = 0

    for gamedata in my_exp_game:
        analytics.append(gamedata)

    if data_to_add.data != []:
        for elem in data_to_add.data:
            data_number.append(elem.check)

    progress = len(data_to_add.data)

    if request.method == 'POST':
        new_number = request.form.get('addnew')
        updated_numb = current_numb + int(new_number)
        for i in range(int(new_number)):
            howMany.append(i+1+current_numb)
        data_to_add.number = updated_numb
        
        try:
            db.session.commit()
            return render_template('tasks.html', 
                new_exp_id=data_to_add.id_table, 
                howMany = howMany, 
                tools=tools,
                quests=quests,
                progress=progress,
                new_exp_name=new_exp_name, 
                number=updated_numb,
                numb=updated_numb,
                data_to_tasks=data_to_add)
        except:
            pass
    else:
        return render_template('tasks.html', 
            new_exp_id=data_to_add.id_table, 
            howMany = howMany, 
            tools=tools, 
            quests=quests,
            progress=progress,
            new_exp_name=new_exp_name,
            number=updated_numb,
            numb=updated_numb,
            data_to_tasks=data_to_add)

@main.route('/dashboard/experiment/<int:row>', methods=['POST','GET'])
@login_required
def dashboard_experiment(row):
    current_u_id = current_user.id
    my_exp_table = UserTable.query.get_or_404(row)
    my_exp_game = Gamedata.query.order_by(Gamedata.id)

    howMany = []
    numb = my_exp_table.number
    tools = my_exp_table.tools.split(',')
    for i in range(numb):
        howMany.append(i+1)
    timer = []
    quest = []
    part_id = []
    analytics = []
    for elem in my_exp_table.data:
        if elem.timer:
            timer.append(elem.timer)
        if elem.quest_file:
            quest.append(elem.quest_file)
        if elem.check:
            part_id.append(elem.check)
    for game in my_exp_game:
        if game.game_data_id == row:
           analytics.append(game)
    
    return render_template('dashboardexp.html', my_exp_table=my_exp_table,
                                                howMany=howMany, 
                                                tools=tools, 
                                                current_u_id=current_u_id, 
                                                row=row, timer = timer, quest = quest, part_id=part_id,
                                                analytics=analytics)


@main.route('/experiments/<int:new_exp_id>', methods=['POST','GET'])
def experiments(new_exp_id):
    data_to_experiment = UserTable.query.get_or_404(new_exp_id)
    
    new_exp_name = data_to_experiment.expname
    quests = data_to_experiment.quests.split(',')
    howMany = []
    numb = data_to_experiment.number
    tools = data_to_experiment.tools.split(',')
    session_number = request.args.get('number')
    for i in range(numb):
        howMany.append(i+1)
    print(quests,flush=True)
    return render_template('experiments.html', new_exp_name=new_exp_name, 
                                               numb=numb, 
                                               new_exp_id=new_exp_id, 
                                               tools=tools, 
                                               number=session_number,
                                               quests=quests)

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

#custom error pages
#invalid url
@main.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

#internal server error
@main.errorhandler(500)
def page_not_found(e):
    return render_template("500.html"), 500