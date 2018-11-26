#!/usr/local/bin/python2
# -*- coding: utf-8 -*-


import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, session, url_for, escape,flash
import datetime
from sqlalchemy.exc import IntegrityError
tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


# DATABASEURI = "sqlite:///test.db"
DB_USER = "jy2930"
DB_PASSWORD = "o0zgg90j"

DB_SERVER = "w4111.cisxo09blonu.us-east-1.rds.amazonaws.com"

DATABASEURI = "postgresql://"+DB_USER+":"+DB_PASSWORD+"@"+DB_SERVER+"/w4111"
engine = create_engine(DATABASEURI)


@app.before_request
def before_request():

  try:
    g.conn = engine.connect()
  except:
    print "uh oh, problem connecting to database"
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):

  try:
    g.conn.close()
  except Exception as e:
    pass


@app.route('/')
def index():

  if not session.get('username'):
    return render_template('login.html')
  else:
    context = dict(username = session['username'],u_id = session['u_id'])
    return render_template("index.html",userinfo = context)
@app.route('/7777777')
def nihaomeile():
 
  if session['identity'] == 'patient':
    command_delete1 = text(''' DELETE FROM patient WHERE u_id = :u_id''')
    g.conn.execute(command_delete1, u_id = session['u_id'])
    command_delete2 = text(''' DELETE FROM "User" WHERE u_id = :u_id''')
    g.conn.execute(command_delete2, u_id = session['u_id'])
  if session['identity'] == 'doctor':
    command_delete1 = text(''' DELETE FROM doctor_affiliate WHERE u_id = :u_id''')
    g.conn.execute(command_delete1, u_id = session['u_id'])
    command_delete2 = text(''' DELETE FROM "User" WHERE u_id = :u_id''')
    g.conn.execute(command_delete2, u_id = session['u_id'])
  session.pop('username')
  return redirect('/')

@app.route('/signup', methods=['GET','POST'])
def signup():
  if request.method == 'GET':
    command_getalldepartment = text(''' SELECT d_id,d_name FROM "DEPARTMENT" ''')
    cursor = g.conn.execute(command_getalldepartment)
    departments = []
    for department in cursor:
      departments.append(dict(d_id = department.d_id,d_name = department.d_name))
    return render_template('signup.html',departments = departments)
  else:
    all_user_name = set([])
    cursor = g.conn.execute('''SELECT username FROM "User" ''')
    for username in cursor:
      all_user_name.add(username[0])
    cursor.close()
    command_uid = text('''SELECT max(u_id) as uidnumber FROM "User" ''')
    cursor = g.conn.execute(command_uid).fetchone()
    u_id = cursor[0] + 1 
    username = request.form.get('username')
    if username in all_user_name:
      error_text = dict(error = 'The username has been used! Please try another one!')
      return render_template('error.html',text = error_text)
    gender = request.form.get('gender')
    password = request.form.get('password')
    email = request.form.get('email')
    birthday = request.form.get('birthday')
    birthday = str(birthday)
    birthday = birthday.split('-')
    year = int(birthday[0])
    month = int(birthday[1])
    day = int(birthday[2])
    birthday = datetime.date(year,month,day)
    identity = request.form.get('identity')
    name = request.form.get('name')
    if request.form.get('departmentid'):
      departmentid = request.form.get('departmentid')

    cmd = text('''INSERT INTO "User" VALUES (:u_id,:username,:gender,:password,:email,:birthday);''')
    g.conn.execute(cmd,u_id = u_id,username = username, gender = gender, password = password,email = email, birthday = birthday)
    if identity =='patient':
      cmd_getpatientpid =text('''SELECT max(p_id) as pid FROM patient ''') 
      cursor = g.conn.execute(cmd_getpatientpid).fetchone()
      p_id = cursor[0] + 1
      cmd_patient = text('''INSERT INTO patient VALUES (:u_id,:p_id,:p_name) ''')
      g.conn.execute(cmd_patient,u_id = u_id,p_id = p_id,p_name = name)
    if identity =='doctor':
      cmd_getdoctordid =text('''SELECT max(d_id) as did FROM doctor_affiliate ''') 
      cursor = g.conn.execute(cmd_getdoctordid).fetchone()
      d_id = cursor[0] + 1
      cmd_doctor = text('''INSERT INTO doctor_affiliate VALUES (:u_id,:d_id,:d_name,:department_id) ''')
      cursor = g.conn.execute(cmd_doctor,u_id = u_id,d_id = d_id,d_name = name,department_id = departmentid)
    # cursor.close()
  return redirect('/')

@app.route('/login',methods=['GET','POST'])
def login():
  if request.method == 'POST':
    username = request.form['username']
    password = request.form['password']

    error = None
    command = text('''SELECT * FROM "User" WHERE username =:x AND password =:y''')
    command = command.bindparams(x = username,y = password)
    user = g.conn.execute(command).fetchone()
    
    
    if user is None:
        error = 'Incorrect username.'
    if error is None:
        session.clear()
        session['username'] = username
        session['u_id'] = user.u_id
        command1 = text('SELECT * from patient WHERE u_id = :u_id')
        cursor = g.conn.execute(command1,u_id = session['u_id']).fetchone()
        patient = cursor
        command2 = text('SELECT * from doctor_affiliate WHERE u_id = :u_id')
        cursor = g.conn.execute(command2,u_id = session['u_id']).fetchone()
        doctor = cursor
        if patient:
          session['identity'] = 'patient'
        if doctor:
          session['identity'] = 'doctor'
        return redirect(url_for('index'))
    flash(error)
    try:
      user.close()
    except:
      pass
  return render_template('/login.html')
@app.route('/logout')
def logout():
  session.pop('username')
  return redirect(url_for('index'))

@app.route('/post/<int:post_id>/<subject>')
def get_post(post_id,subject):
  command = text('SELECT * from post_make WHERE post_id = :post_id AND subject = :subject ')
  cursor = g.conn.execute(command,post_id = post_id, subject = subject)
  post = []
  for n in cursor:
    commendfindusername1=text('SELECT p_name from patient WHERE u_id = :u_id')
    cursor = g.conn.execute(commendfindusername1,u_id = n.u_id).fetchone()
    if cursor:
      name = cursor[0]
    commendfindusername2=text('SELECT d_name from doctor_affiliate WHERE u_id = :u_id')
    cursor = g.conn.execute(commendfindusername2,u_id = n.u_id).fetchone()
    if cursor:
      name = cursor[0]

    post.append(dict(subject = n.subject, post_id = n.post_id,content =n.content,tags = n.tags,posttime = n.posttime,name=name))
  return render_template('post.html',post = post)
@app.route('/posts/')
def get_all_posts():
  command = text('SELECT post_id,subject FROM post_make')
  cursor = g.conn.execute(command)
  posts = []
  for post in cursor:
    posts.append(dict(subject = post.subject, post_id = post.post_id))
  cursor.close()
  return render_template('posts.html', posts=posts)

@app.route('/make_post',methods = ['GET','POST'])
def make_post():
  if request.method == 'GET':
    return render_template('makepost.html')
  else:
    command_getpostnumber = text(''' SELECT max(post_id) FROM post_make''')
    cursor = g.conn.execute(command_getpostnumber).fetchone()
    post_id = cursor[0]+1
    u_id = session['u_id']
    postdate = datetime.datetime.now().strftime("%Y-%m-%d")
    postdate = postdate.split('-')
    year = int(postdate[0])
    month = int(postdate[1])
    day = int(postdate[2])
    postdate = datetime.date(year,month,day)
    tags = request.form['tags']
    content = request.form.get('content')
    subject = request.form.get('subject')
    if subject is not None:
      cmd = text('''INSERT INTO post_make VALUES (:post_id,:u_id,:posttime,:tags,:content,:subject) ''')
      cursor = g.conn.execute(cmd,post_id = post_id,u_id = u_id, posttime= postdate,tags = tags, content = content, subject = subject)
      cursor.close()
      return redirect('/posts/')
    else:
      error = "Subject could not be None!"
      texterror = dict(error = error)
      return render_template('error.html',text = texterror)
@app.route('/add_illness',methods = ['GET','POST'])
def add_illness():
  if session['identity'] == 'patient':
    error = "Oh oh, you are not a doctor"
    texterror = dict(error = error)
    return render_template('error.html',text = texterror)
  if request.method == 'GET':
    commmand_getallpatient = text(''' SELECT u_id,p_name FROM patient''')
    cursor = g.conn.execute(commmand_getallpatient)
    patients = []
    for patient in cursor:
      patients.append(dict(u_id = patient.u_id,p_name = patient.p_name))
    commmand_getalldisease = text(''' SELECT disease_id, disease_name FROM disease''')
    cursor = g.conn.execute(commmand_getalldisease)
    diseases = []
    for disease in cursor:
      diseases.append(dict(d_id = disease.disease_id, d_name = disease.disease_name))
    cursor.close()

    return render_template('addillness.html',patients = patients, diseases = diseases)
  else:
    command_getillnessnumber = text(''' SELECT max(i_id) FROM illness''')
    cursor = g.conn.execute(command_getillnessnumber).fetchone()
    i_id = cursor[0]+1
    p_id = request.form.get('patient')
    disease_id = request.form.get('disease_id')

    startdate = request.form.get('startdate')
    startdate = str(startdate)
    startdate = startdate.split('-')
    startyear = int(startdate[0])
    startmonth = int(startdate[1])
    startday = int(startdate[2])
    startdate = datetime.date(startyear,startmonth,startday)
    enddate = request.form.get('enddate')
    enddate = str(enddate)
    enddate = enddate.split('-')
    endyear = int(enddate[0])
    endmonth = int(enddate[1])
    endday = int(enddate[2])
    enddate = datetime.date(endyear,endmonth,endday)

    command_addillness = text(''' INSERT INTO illness VALUES (:i_id,:p_id,:disease_id,:start_time,:end_time)''')

    cursor = g.conn.execute(command_addillness,i_id = i_id,p_id = p_id, disease_id = disease_id, start_time = startdate,end_time = enddate)
    cursor.close()
    return  redirect('/')
@app.route('/add_cure',methods = ['GET','POST'])
def add_cure():
  if session['identity'] == 'patient':
    error = "Oh oh, you are not a doctor"
    texterror = dict(error = error)
    return render_template('error.html',text = texterror)
  if request.method == 'GET':
    commmand_getallillness = text(''' SELECT i_id FROM illness''')
    cursor = g.conn.execute(commmand_getallillness)
    illnesses = []
    for illness in cursor:
      illnesses.append(dict(i_id = illness.i_id))
    cursor.close()
    return render_template('addcure.html',illnesses = illnesses)
  else:
    d_id = session['u_id']
    i_id = request.form.get('i_id')
    curetime = request.form.get('cure_time')
    curedate = str(curetime)
    curedate = curedate.split('-')
    cureyear = int(curedate[0])
    curemonth = int(curedate[1])
    cureday = int(curedate[2])
    curedate = datetime.date(cureyear,curemonth,cureday)
    drugs = request.form.get('drugs')
    surgery = request.form.get('surgery')

    command_addcure = text(''' INSERT INTO cure VALUES (:d_id,:i_id,:time, :drugs,:surgery)''')
    try:
      cursor = g.conn.execute(command_addcure,d_id = d_id, i_id = i_id, time = curedate, drugs = drugs, surgery = surgery)
    except IntegrityError:
      error_text = 'IntegrityError: (psycopg2.IntegrityError) duplicate key value violates unique constraint "cure_pkey" DETAIL:  Key (d_id, i_id)=(1002, 1) already exists!'
      error_text = dict(error = error_text)
      return render_template('error.html',text = error_text)
    cursor.close()
    return redirect('/')

@app.route('/<int:u_id>/<username>')
def profile(u_id,username):
  command1 = text('SELECT * from patient WHERE u_id = :u_id')
  cursor = g.conn.execute(command1,u_id = u_id).fetchone()
  patient = cursor
  command2 = text('SELECT * from doctor_affiliate WHERE u_id = :u_id')
  cursor = g.conn.execute(command2,u_id = u_id).fetchone()
  doctor = cursor
  command_post = text('SELECT * from post_make WHERE u_id = :u_id')
  cursor = g.conn.execute(command_post,u_id = u_id)
  posts = []
  for post in cursor:
    posts.append(dict(subject = post.subject, post_id = post.post_id))
  if patient:
    command_illness = text('SELECT i_id,disease_name,start_time,end_time from illness as I,disease as D WHERE p_id = :u_id AND I.disease_id = D.disease_id')
    cursor = g.conn.execute(command_illness,u_id = u_id)
    illnesses = []
    for illness in cursor:
      illnesses.append(dict(i_id = illness.i_id,disease_name=illness.disease_name,start_time=illness.start_time,end_time = illness.end_time))
    cursor.close()
    return render_template('profile_patient.html',posts= posts,illnesses = illnesses)
  if doctor:
    command_cure = text('SELECT i_id,time,drugs,surgery from cure  WHERE d_id = :u_id')
    cursor = g.conn.execute(command_cure,u_id = u_id)
    cures = []
    for cure in cursor:
      cures.append(dict(i_id = cure.i_id,time = cure.time,drugs =cure.drugs,surgery = cure.surgery ))
    cursor.close()
    return render_template('profile_doctor.html',posts = posts, cures = cures)

@app.route('/ratings')
def rating():
  command = text(''' SELECT  D.d_id, R.rating, D.d_name as d_name FROM doctor_affiliate as D LEFT OUTER JOIN (
            SELECT D.u_id as d_id,avg(R.rating) as rating FROM doctor_affiliate as D,rate as R WHERE R.d_id = D.u_id GROUP BY D.u_id) as R 
            ON D.u_id = R.d_id''')
  cursor = g.conn.execute(command)
  ratings = []
  for rating in cursor:
    ratings.append(dict(u_id = rating.d_id,rating = rating.rating, d_name = rating.d_name))
  cursor.close()

  return render_template('ratings.html',ratings = ratings)

@app.route('/search_rating',methods=['POST','GET'])
def search_rating():
  doctor_name = request.form['name']
  command = text(''' SELECT  D.d_id, R.rating, D.d_name as d_name FROM doctor_affiliate as D ,rate as R where  D.u_id = R.d_id AND D.d_name = :name ''')
  cursor = g.conn.execute(command, name = doctor_name)
  doctor_rating = []
  for rating in cursor:
    doctor_rating.append(dict(u_id = rating.d_id,rating = rating.rating, d_name = rating.d_name))
  cursor.close()

  return render_template('ratings.html',ratings = doctor_rating)




@app.route('/addrating',methods = ['GET','POST'])
def addrating():
  if session['identity'] == 'doctor':
    error = "Oh oh, you are not a patient"
    texterror = dict(error = error)
    return render_template('error.html',text = texterror)
  if request.method == 'GET':
    commmand_getalldoctors = text(''' SELECT u_id,d_name FROM doctor_affiliate''')
    cursor = g.conn.execute(commmand_getalldoctors)
    doctors = []
    for doctor in cursor:
      doctors.append(dict(u_id = doctor.u_id,d_name = doctor.d_name))
    cursor.close()
    return render_template('addrating.html',doctors = doctors)
  else:
    p_id = session['u_id']
    d_id = request.form.get('d_id')
    rating = request.form.get('rating')
    command_addrating = text(''' INSERT INTO rate VALUES (:p_id,:d_id,:rating)''')
    cursor = g.conn.execute(command_addrating,p_id = p_id,d_id = d_id,rating=rating)
    cursor.close()
    return redirect('/')

@app.route('/department')
def Department():
  print request.args
  cursor = g.conn.execute('''SELECT * FROM "DEPARTMENT"''')
  department = []
  for result in cursor:
    department.append(result)
  cursor.close()
  return render_template("department.html", data = department, length = len(department))

@app.route('/department/<d_id>')
def Disease_of_Department(d_id):
  print request.args
  cmd = 'SELECT * FROM disease WHERE department_id = :id'
  cursor = g.conn.execute(text(cmd), id = d_id)
  Disease_of_Department = []
  for result in cursor:
    Disease_of_Department.append(result[:])
  cursor.close()
  return render_template("disease.html", data = Disease_of_Department, length = len(Disease_of_Department), d_id = d_id)

@app.route('/patient')
def patient():
  print request.args
  cursor = g.conn.execute('''SELECT * FROM patient''')
  patient = []
  for result in cursor:
    patient.append(result[:])
  cursor.close()
  return render_template("all_patients.html", data = patient, length = len(patient))


@app.route('/doctor')
def doctor():
  print request.args
  cursor = g.conn.execute('''SELECT doctor_affiliate.*, "DEPARTMENT".d_name FROM doctor_affiliate,"DEPARTMENT" WHERE doctor_affiliate.department_id = "DEPARTMENT".d_id''')
  doctor = []
  for result in cursor:
    doctor.append(result[:])
  cursor.close()
  return render_template("all_doctors.html", data = doctor, length = len(doctor))
@app.route('/disease/<disease_id>')
def Symptom_of_Disease(disease_id):
  print request.args
  cmd = 'SELECT * FROM disease_with_symptom WHERE disease_id = :id'
  cursor = g.conn.execute(text(cmd), id = disease_id)
  Symptom_of_Disease = []
  for result in cursor:
    Symptom_of_Disease.append(result[:])
  cursor.close()
  return render_template("symptom.html", data = Symptom_of_Disease, length = len(Symptom_of_Disease) , di_id = disease_id)


@app.route('/symptom')
def diseasewithsymptom():
  print request.args
  cursor = g.conn.execute('SELECT DISTINCT s_id,s_name FROM disease_with_symptom ORDER BY s_id ASC')
  symptoms = []
  for result in cursor:
    symptoms.append(result[:])
  cursor.close()
  return render_template("all_symptoms.html", data = symptoms, type = 'All Symptoms', length = len(symptoms))

@app.route('/all_symptoms/<symptom_id>')
def Disease_of_Symptom(symptom_id):
  print request.args
  cmd = 'SELECT disease.disease_id,disease.disease_name,disease.treatment,disease.cause,department.d_name FROM disease_with_symptom,disease,"DEPARTMENT" department WHERE disease_with_symptom.s_id = :id AND disease.department_id = department.d_id AND disease_with_symptom.disease_id =disease.disease_id'
  cursor = g.conn.execute(text(cmd), id = symptom_id)
  Disease_of_Symptom = []
  for result in cursor:
    Disease_of_Symptom.append(result[:])
  cursor.close()
  return render_template("diseasewithsymptom.html", data = Disease_of_Symptom, length = len(Disease_of_Symptom) , symptom_id = symptom_id)

@app.route('/cure')
def cure():
  command_cure = text('SELECT i_id,time,drugs,surgery from cure')
  cursor = g.conn.execute(command_cure)
  cures = []
  for cure in cursor:
    cures.append(dict(i_id = cure.i_id,time = cure.time,drugs =cure.drugs,surgery = cure.surgery ))
  cursor.close()
  return render_template('cure.html',cures = cures)

@app.route('/search_cure',methods=['POST'])
def search_cure():
  doctor_name = request.form['name']
  command = text(''' SELECT  D.d_id,D.d_name,C.i_id,C.time,C.drugs,C.surgery FROM doctor_affiliate as D ,cure as C where  D.u_id = C.d_id AND D.d_name = :name ''')
  cursor = g.conn.execute(command, name = doctor_name)
  doctor_cures = []
  for cure in cursor:
    doctor_cures.append(dict(d_id = cure.d_id, d_name = cure.d_name,i_id = cure.i_id,time = cure.time,drugs =cure.drugs,surgery = cure.surgery ))
  cursor.close()
  return render_template('cure_search.html',cures = doctor_cures, doctor_name = doctor_name)



@app.route('/add_department', methods=['POST','GET'])
def add_department():

  result_name = request.form['name']
  result_context = request.form['context']
  cursor = g.conn.execute('SELECT max(d_id) FROM "DEPARTMENT"')
  x = cursor.fetchone()
  new_id = x[0] + 1
  cursor.close()
  cmd = 'INSERT INTO "DEPARTMENT" VALUES (:id,:name,:context)'
  g.conn.execute(text(cmd), id = new_id , name = result_name, context = result_context)
  return redirect('/department')


@app.route('/add_disease/<d_id>', methods=['POST','GET'])
def add_disease(d_id):
  result_name = request.form['name']
  result_treatment = request.form['treatment']
  result_cause = request.form['cause']
  cursor = g.conn.execute('SELECT max(disease_id) FROM disease')
  x = cursor.fetchone()
  disease_id = x[0] + 1
  cursor.close()
  cmd = 'INSERT INTO disease VALUES (:disease_id,:name,:treatment,:cause,:department_id)'
  g.conn.execute(text(cmd), disease_id = disease_id , name = result_name, treatment = result_treatment, cause = result_cause, department_id = d_id)
  return redirect('/department')


@app.route('/add_symptom/<di_id>', methods=['POST','GET'])
def add_symptom(di_id):
  result_name = request.form['name']
  cursor = g.conn.execute('SELECT max(s_id) FROM disease_with_symptom')
  x = cursor.fetchone()
  s_id = x[0]+1
  cursor.close()
  cmd = 'INSERT INTO disease_with_symptom VALUES (:disease_id,:s_id,:name)'
  g.conn.execute(text(cmd), disease_id = di_id , s_id = s_id,name = result_name)
  return redirect('/symptom')





if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):


    HOST, PORT = host, port
    print "running on %s:%d" % (HOST, PORT)
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


  run()
