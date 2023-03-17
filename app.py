import os
from flask import Flask, render_template, request, url_for, redirect, flash
import sqlite3
from werkzeug.utils import secure_filename
from flask_wtf import FlaskForm
from wtforms import StringField, RadioField
from wtforms.validators import InputRequired, Length

SECRET_KEY =os.urandom(32)

conn = sqlite3.connect('SnMDB.sqlite')
c = conn.cursor()
c.close()

# Initialise Flask app
app = Flask(__name__, template_folder='templates')
# app = Flask("__maintenance_app__")
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # 16 MB max file size
app.config['SECRET_KEY'] = SECRET_KEY
# Define allowed file extensions for picture upload
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}



class SafetyReportForm(FlaskForm):
    student_number = StringField('Student number', validators=[InputRequired()])
    staff_number = StringField('Staff number', validators=[InputRequired()])
    report_number = StringField('Report number', validators=[InputRequired()])
    title = StringField('Title', validators=[InputRequired()])
    description = StringField('Describe the issue', validators=[InputRequired(), Length(max=200)])
    suggestion = StringField('Suggest the solution you want to see implemented')
    campus = StringField('Campus', validators=[InputRequired()])
    location = StringField('Location', validators=[InputRequired()])
    urgency = RadioField('Urgency', choices=[('high', 'High'), ('medium', 'Medium'), ('low', 'Low')], validators=[InputRequired()])


@app.route('/')
def home():
    return render_template('home.html')

@app.route("/index")
def index():
  return render_template("Contact.html")

# Define route for the Maintenance Report page
@app.route('/maintenance', methods=['GET', 'POST'])
def maintenance_report():
    # Check if request method is POST
    if request.method == 'POST':
        # Get form inputs
        student_number = request.form['student_number']
        staff_number = request.form['staff_number']
        title = request.form['title']
        # requirement1 = request.form['requirement1']
        # requirement2 = request.form['requirement2']
        description = request.form['description']
        suggestion = request.form['suggestion']
        infrastructure = request.form['infrastructure']
        campus = request.form['campus']
        floor = request.form['floor']
        venue_type = request.form['venue_type']
        venue_number = request.form['venue_number']

        # Check if either student number or staff number is provided
        if not student_number and not staff_number:
            return render_template('maintenance_report.html', error='Please provide either Student Number or Staff Number')

        # Check if picture upload is provided and allowed file extension
        if 'picture_upload' not in request.files:
            return render_template('maintenance_report.html', error='Please provide a picture upload')
        picture_upload = request.files['picture_upload']
        if not picture_upload.filename:
            return render_template('maintenance_report.html', error='Please provide a picture upload')
        if not allowed_file(picture_upload.filename):
            return render_template('maintenance_report.html', error='Picture upload must be a JPG, JPEG, PNG, or GIF file')

        # Secure filename and save uploaded picture
        picture_filename = secure_filename(picture_upload.filename)
        picture_upload.save(os.path.join(app.config['UPLOAD_FOLDER'], picture_filename))

        # Check if description and suggestion are not longer than 200 characters
        if len(description) > 200:
            return render_template('maintenance_report.html', error='Description must be 200 characters or less')
        if len(suggestion) > 200:
            return render_template('maintenance_report.html', error='Suggestion must be 200 characters or less')

        # Process Maintenance Report data
        # Here you can write the code to process the Maintenance Report data,
        # such as storing it in a database or sending it via email.

        # Render success page
        return redirect(url_for('maintenance_report_success'))

    else:
        # Render Maintenance Report form
        return render_template('maintenance_report.html')


@app.route("/safety-report", methods=['POST' , 'GET'])
def safety_report():
    form = SafetyReportForm()
    if request.method=="POST":
    
        SStudNo = request.form.get("student_number")
        SStaffNo = request.form.get("staff_number")
        STitle = request.form.get("title")
        SDescription = request.form.get("description")
        SSolution = request.form.get("suggestion")
        SCampus = request.form.get("campus")
        SLocation = request.form.get("Location")
        SUrgency = request.form.get("urgency")
        radio = request.form.get('user_type')
        if radio == "student":
            conn = sqlite3.connect("SnMDB.sqlite")
            cur = conn.cursor()
            cur.execute('''INSERT INTO tbl_SafteyR(SStudStaffNo, STitle, SDescription, SSolution, SCampus, SLocation, SUrgency, StatusOfReport)VALUES(?, ?, ?, ?, ?, ?, ?, ?)''',
                (SStudNo, STitle, SDescription, SSolution,SCampus, SLocation, SUrgency, "Sent"))
            conn.commit()
            conn.close()
            flash('Report was successfully submitted', 'success')
            return redirect(url_for("view_reports"))
        if radio == "staff":
            conn = sqlite3.connect("SnMDB.sqlite")
            cur = conn.cursor()
            cur.execute('''INSERT INTO tbl_SafteyR(SStudStaffNo, STitle, SDescription, SSolution, SCampus, SLocation, SUrgency, StatusOfReport)VALUES(?, ?, ?, ?, ?, ?, ?, ?)''',
                (SStaffNo, STitle, SDescription, SSolution,SCampus, SLocation, SUrgency, "Sent"))
            conn.commit()
            conn.close()
            flash('Report was successfully submitted', 'success')
            return redirect(url_for("View"))
        print("Failed to insert data into table:", error)
        flash('Failed to submit report', error)
    return render_template('safety_report.html')

def get_db():
    conn = sqlite3.connect('SnMDB.sqlite')
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/View", methods=['GET'])
def view_reports():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''SELECT * FROM tbl_SafteyR''')
    reports = cur.fetchall()
    conn.close()
    return render_template('View.html', reports=reports)


@app.route("/safety_report", methods=['GET','POST'])
def safety_report_():
    form = SafetyReportForm()
    if request.method == 'POST' and form.validate():
        if form.validate_on_submit():
            return submit_safety_report(form)
        return 'Report submitted successfully'
    return render_template('safety_report.html', form=form)

@app.route('/maintenance_report/success')
def maintenance_report_success():
    # Render success page
    return render_template('maintenance_report_success.html')

# Define function to check allowed file extensions for picture upload
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/login', methods=['POST', 'GET'])
def login():
   if request.method=='POST':
      fieldStaff = request.form.get('StaffNo')
      fieldStudent = request.form.get('StudentNo')
      fieldEmail=request.form.get('EmailAdress')
      fieldPassword=request.form.get('Password')
      radio=request.form.get('options')
      def check_email_exists(fieldStaff, fieldStudent, fieldEmail, fieldPassword):
      #checking if staff member exists
         if radio == "option1":
            conn=sqlite3.connect('SnMDB.sqlite')
            c=conn.cursor()
            c.execute("SELECT COUNT(*)FROM tbl_LoginSignUp WHERE (StaffNo, EmailAdress, Password)=(?, ?, ?)",(fieldStaff, fieldEmail, fieldPassword))
            result=c.fetchone()[0]
            c.close()
            return result
         if radio == "option2":
            conn=sqlite3.connect('SnMDB.sqlite')
            c=conn.cursor()
            c.execute("SELECT COUNT(*)FROM tbl_LoginSignUp WHERE (StudentNo, EmailAdress, Password)=(?, ?, ?)",(fieldStudent, fieldEmail, fieldPassword))
            result=c.fetchone()[0]
            c.close()
            return result
      result=check_email_exists(fieldStaff, fieldStudent, fieldEmail, fieldPassword)#calling check email method
      if result>0:
         return redirect(url_for("home"))
      else:
         return redirect(url_for("login"))
   return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST': #Getting the data
        staff_number = request.form['StaffNo']
        student_number = request.form['StudentNo']
        email = request.form['EmailAdress']
        password = request.form['Password']
        domain = email.split('@')[-1]
        username = email.split('@')[0]

        radio = request.form.get('options') #Get information from inputs
        fieldStaffNo = request.form.get('StaffNo')
        fieldStudentNo = request.form.get('StudentNo')
        fieldPassword = request.form.get('Password')
        

        def check_email_exists(email): #chacking if the email entered already exists
            conn = sqlite3.connect('SnMDB.sqlite')
            c = conn.cursor()
            c.execute('''SELECT COUNT(*) FROM tbl_LoginSignUp WHERE EmailAdress = ?''', (email,))
            result = c.fetchone()[0]
            c.close()
            return result
        
        result = check_email_exists(email) #calling check email method

        if radio == 'option1' and ((not fieldStaffNo and fieldStudentNo) or 
                                   (not fieldStaffNo and not fieldStudentNo) or
                                   (fieldStaffNo and fieldStudentNo)):  #Validating correct information entered
            return 'Please enter information in all the necessary fields. Unless you are a tutor you must not have both staff number and student number entered.', render_template('register.html')
        elif radio == 'option1' and (domain == 'dut.ac.za' and len(fieldStaffNo) == 8 and len(fieldPassword) >= 8 and result == 0): #Validation email address for staff(correct email domain)
                conn = sqlite3.connect('SnMDB.sqlite')
                c = conn.cursor()
                c.execute('''INSERT INTO tbl_LoginSignUp (StaffNo, StudentNo, EmailAdress, Password) VALUES (?, ?, ?, ?)''',
                        (staff_number, student_number, email, password)) #Adding new staff member into db
                conn.commit()
                conn.close()
                return redirect(url_for("home")) #Back to home page
        elif radio == 'option1' and ((domain != 'dut.ac.za' and len(fieldStaffNo) != 8 and len(fieldPassword) < 8)or 
                                     (domain != 'dut.ac.za' and len(fieldStaffNo) == 8 and len(fieldPassword) >= 8) or 
                                     (domain == 'dut.ac.za' and len(fieldStaffNo) != 8 and len(fieldPassword) >= 8) or
                                     (domain != 'dut.ac.za' and len(fieldStaffNo) != 8 and len(fieldPassword) >= 8) or
                                     (domain != 'dut.ac.za' and len(fieldStaffNo) == 8 and len(fieldPassword) < 8) or
                                     (domain == 'dut.ac.za' and len(fieldStaffNo) != 8 and len(fieldPassword) < 8) or
                                     (domain == 'dut.ac.za' and len(fieldStaffNo) == 8 and len(fieldPassword) < 8) or
                                     (result > 0)): #If staff email domain wrong, redirect to signup page
                return redirect(url_for("signup")) #Refreshes sign up page
        
        
        if (radio == 'option2') and ((not fieldStudentNo and fieldStaffNo) or 
                                   ( fieldStudentNo and fieldStaffNo) or 
                                   (not fieldStudentNo and not fieldStaffNo)): #Validating correct information entered
            return 'Unless you are a staff member or a tutor at DUT, you must only enter your student number in the student number field to register.', render_template('register.html')
        elif (radio == 'option2') and (domain == 'dut4life.ac.za' and username == fieldStudentNo and len(fieldStudentNo) == 8 and len(fieldPassword) >= 11 and result == 0): #Validation email address for student(correct email)
                conn = sqlite3.connect('SnMDB.sqlite')
                c = conn.cursor()
                c.execute('''INSERT INTO tbl_LoginSignUp (StaffNo, StudentNo, EmailAdress, Password) VALUES (?, ?, ?, ?)''',
                        (staff_number, student_number, email, password))#Adding new student into db
                conn.commit()
                conn.close()
                return redirect(url_for("home"))
        else: #If student wrong, redirect to signup page
            return redirect(url_for("signup")) 
        
    return render_template('register.html')

if __name__ == '__main__':
    app.run(debug=True)