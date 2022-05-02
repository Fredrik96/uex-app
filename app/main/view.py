import pandas as pd
from fitbit.exceptions import BadResponse
from flask import flash, jsonify, url_for, redirect, render_template, request, Response
from flask_login import logout_user, login_required, login_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta, time

from app import db
from app.fitbit_client import fitbit_client, get_permission_screen_url, do_fitbit_auth
from forms import RegisterForm, LoginForm, DashboardForm
from app.models import User, UserTable, UserData, get_user_fitbit_credentials
from . import main

import cv2
from camera import VideoCamera

video_camera = None
global_frame = None

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
            #if new_exp.id_table != 1:
                #print(new_exp.id_table, flush=True)
                #sql = "ALERT TABLE datatable AUTO_INCREMENT=1"
                #mycursor = db.engine
                #mycursor.execute(sql)
            db.session.add(new_exp)
            db.session.expire_on_commit=False
            db.session.commit()
            new_exp_id = new_exp.id_table
            return redirect(url_for('main.tasks', parttakers=mychecks.number, tools=mychecks.tools, new_exp_id=new_exp_id))
        else:
            flash(u'You need to specify at least 1 tool and include 1 participant', 'info')
            return redirect(url_for('main.profile'))

    user_profile = "Could not access fitbit profile"
    fitbit_creds = get_user_fitbit_credentials(current_user.id)
    if fitbit_creds:
        with fitbit_client(fitbit_creds) as client:
            try:#delete token if expired or no longer valid
                # db.session.query(FitbitToken).delete()
                # db.session.commit()
                profile_response = client.user_profile_get()
                user_profile = "{} has been on fitbit since {}".format(
                    profile_response['user']['fullName'],
                    profile_response['user']['memberSince']
                )
            except BadResponse:
                print("Api Call Failed", flush=True)
    return render_template('profile.html', name=current_user.username, user_profile=user_profile, permission_url=get_permission_screen_url())

@main.route('/oauth-redirect', methods=['GET'])
@login_required
def handle_redirect():
    code = request.args.get('code')
    try:
        do_fitbit_auth(code, current_user)
    except:
        print('Not able to do fitbit auth!', flush=True)
        redirect(url_for('main.profile'))
    return redirect(url_for('main.profile'))

@main.route('/quest/<int:new_exp_id>', methods=['GET','POST'])
@login_required
def quest(new_exp_id):
    current_u_id = current_user.id
    questions = []
    data_to_quest = UserTable.query.get_or_404(new_exp_id)

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
                my_exp = UserTable.query.order_by(UserTable.id_table)
                return redirect(url_for('main.dashboard', my_exp=my_exp, current_u_id=current_u_id))
    return render_template('questionnaire.html', new_exp_id=data_to_quest.id_table)


@main.route('/record_status/<int:number>', methods=['POST'])
@login_required
def record_status(number):
    global video_camera
    if video_camera == None:
        video_camera = VideoCamera(number)

    json = request.get_json()
    status = json['status']

    if status == "true":
        if video_camera == None:
            video_camera.start_cam()
        print("recording", flush=True)
        video_camera.start_record(number)
        return jsonify(result="started")
    else:
        video_camera.stop_record()
        print(video_camera.is_open,flush=True)
        return jsonify(result="stopped")

def video_stream(number):
    global video_camera 
    global global_frame
    
    if video_camera == None:
        video_camera = VideoCamera(number)
        
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
        

@main.route('/video_viewer/<int:number>')
def video_viewer(number):
    return Response(video_stream(number), mimetype='multipart/x-mixed-replace; boundary=frame')

@main.route('/recording/<int:number>')
@login_required
def recording(number):
    file = ["video{}.mp4".format(str(number))]
    return render_template('recording.html', file=file, number=number)

@main.route('/tasks/<int:new_exp_id>', methods=['POST','GET'])
@login_required
def tasks(new_exp_id):
    #declare some variables to avoid undefined when reloading page
    data_to_tasks = UserTable.query.get_or_404(new_exp_id)
    howMany = []
    numb = data_to_tasks.number
    tools = data_to_tasks.tools.split(',')
    for i in range(numb):
        howMany.append(i+1)
    
    if request.method == 'POST':
        #getting the session data in order to change the html according to who is in session
        if request.form.get('next') == 'Next Page':
            if "quest" in data_to_tasks.tools:
                return redirect(url_for('main.quest', new_exp_id=data_to_tasks.id_table))
            else:
                current_u_id = current_user.id
                my_exp = UserTable.query.order_by(UserTable.id_table)
                return redirect(url_for('main.dashboard', my_exp=my_exp, current_u_id=current_u_id))
    return render_template('tasks.html', tools=tools,
                                         new_exp_id=data_to_tasks.id_table,
                                         howMany = howMany,
                                         toolsstr=data_to_tasks.tools)

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
        print(timer,flush=True)
        if(timer!=""):    
            new_data = UserData(timer=timer, users_table_id=data_table.id_table)
            db.session.add(new_data)
            db.session.commit()
            print("Timer commited to UserData", flush=True)
    return render_template('tasks.html',tools=tools,
                                        new_exp_id=data_table.id_table,
                                        howMany = howMany,numb = numb)

@main.route('/process/<int:new_exp_id>', methods=['POST'])
def process(new_exp_id):
    data_table = UserTable.query.get_or_404(new_exp_id)
    howMany = []
    numb = data_table.number
    tools = data_table.tools.split(',')
    for i in range(numb):
        howMany.append(i+1)

    if request.method == 'POST':
        in_session = request.form.get('session')

        if in_session != None:
            return jsonify({'in_session' : in_session})
        # if request.form.get('startcardio') != None:
        #     today = str((datetime.now()- timedelta(hours=20)).strftime("%Y-%m-%d"))
        #     fitbit_creds = get_user_fitbit_credentials(current_user.id)
        #     if fitbit_creds:
        #         with fitbit_client(fitbit_creds) as client:
        #             fitbit_statsHR = client.intraday_time_series('activities/heart', base_date=today, detail_level='1sec')
        #             fitbit_statsHR1 = client
        #     time_list = []
        #     val_list = []
        #     for i in fitbit_statsHR['activities-heart-intraday']['dataset']:
        #         val_list.append(i['value'])
        #         time_list.append(i['time'])
        #     heartdf = pd.DataFrame({'Heart Rate':val_list,'Time':time_list})
        #     print(heartdf.head(10).to_html(),flush=True)
        #     hr_html = heartdf.head(10).to_html(classes='table table-stripped')
    return render_template('tasks.html',tools=tools,
                                        new_exp_id=data_table.id_table,
                                        howMany = howMany,
                                        numb=numb)

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
    current_numb = data_to_add.number
    tools = data_to_add.tools.split(',')
    howMany = []

    if request.method == 'POST':
        new_number = request.form.get('addnew')
        updated_numb = current_numb + int(new_number)
        for i in range(int(new_number)):
            howMany.append(i+1+current_numb)
        data_to_add.number = updated_numb
        print(updated_numb, flush=True)
        try:
            db.session.commit()
            return render_template('tasks.html', 
                new_exp_id=data_to_add.id_table, 
                howMany = howMany, 
                tools=tools, toolsstr = 
                data_to_add.tools)
        except:
            return render_template('tasks.html', 
                new_exp_id=data_to_add.id_table, 
                howMany = howMany, 
                tools=tools, 
                toolsstr = data_to_add.tools)
    else:
        return render_template('tasks.html', 
            new_exp_id=data_to_add.id_table, 
            howMany = howMany, 
            tools=tools, 
            toolsstr = data_to_add.tools)

@main.route('/dashboard/experiment/<int:row>', methods=['POST','GET'])
@login_required
def dashboard_experiment(row):
    current_u_id = current_user.id
    my_exp = UserTable.query.get_or_404(row)
    my_exp2 = UserData.query.filter_by(users_table_id = my_exp.id_table)

    howMany = []
    numb = my_exp.number
    tools = my_exp.tools.split(',')
    for i in range(numb):
        howMany.append(i+1)
    print(my_exp.data,flush=True)

    if request.method == "POST":
        hr = request.form.get("hrmeter")
        print(hr,flush=True)
            
    return render_template('dashboardexp.html', my_exp=my_exp, my_exp2=my_exp2, howMany=howMany, tools=tools, current_u_id=current_u_id, row=row)

@main.route('/indexing')
def indexing():  
    return render_template('indexing.html')

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))

#custom error pages
#invalid url
@main.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

#internal server error
@main.errorhandler(500)
def page_not_found(e):
    return render_template("500.html"), 500