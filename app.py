from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
import secrets
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = secrets.token_hex(8)  # Needed for session management

# Configure Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'teachersapp2024@gmail.com'
app.config['MAIL_PASSWORD'] = 'ppeeaywbxlrcplzt'
app.config['MAIL_DEFAULT_SENDER'] = 'teachersapp2024@gmail.com'

mail = Mail(app)

# Configure Flask-SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///teachers.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define the User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)

teachers = ["Marija Trajanoska", "Eli Zarlinova", "Teona Angelovska"]
teacher_emails = {
    "Marija Trajanoska": "macatrajanoska8@gmail.com",
    "Eli Zarlinova": "elizarlinova02@gmail.com",
    "Teona Angelovska": "teonaangelovska@gmail.com",
}

# Sample data for teachers and their schedules
teacher_schedules = {
    "Marija Trajanoska": {
        "08:00": {"Monday": "Math", "Tuesday": "", "Wednesday": "", "Thursday": "", "Friday": ""},
        "10:00": {"Monday": "", "Tuesday": "", "Wednesday": "", "Thursday": "", "Friday": ""},
        "12:00": {"Monday": "Research Meeting", "Tuesday": "Teachers' Council", "Wednesday": "", "Thursday": "", "Friday": ""},
        "14:00": {"Monday": "", "Tuesday": "", "Wednesday": "", "Thursday": "", "Friday": ""},
        "16:00": {"Monday": "", "Tuesday": "", "Wednesday": "Biology", "Thursday": "", "Friday": ""}
    },
    "Eli Zarlinova": {
        "08:00": {"Monday": "", "Tuesday": "", "Wednesday": "Physics", "Thursday": "", "Friday": ""},
        "10:00": {"Monday": "", "Tuesday": "", "Wednesday": "", "Thursday": "", "Friday": ""},
        "12:00": {"Monday": "", "Tuesday": "Teachers' Council", "Wednesday": "", "Thursday": "", "Friday": ""},
        "14:00": {"Monday": "", "Tuesday": "", "Wednesday": "", "Thursday": "", "Friday": "Grades administrative"},
        "16:00": {"Monday": "", "Tuesday": "", "Wednesday": "", "Thursday": "", "Friday": ""}
    },
    "Teona Angelovska": {
        "08:00": {"Monday": "", "Tuesday": "", "Wednesday": "History", "Thursday": "", "Friday": ""},
        "10:00": {"Monday": "", "Tuesday": "Project Presentation", "Wednesday": "", "Thursday": "", "Friday": ""},
        "12:00": {"Monday": "Geography", "Tuesday": "Teachers' Council", "Wednesday": "", "Thursday": "", "Friday": ""},
        "14:00": {"Monday": "", "Tuesday": "", "Wednesday": "", "Thursday": "", "Friday": "Meeting"},
        "16:00": {"Monday": "", "Tuesday": "", "Wednesday": "", "Thursday": "", "Friday": ""}
    }
}

requests = []

@app.route('/')
def index():
    if 'user_id' not in session:
        return render_template('login.html')
    return render_template("index.html", teachers=teachers)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('index'))
        return 'Invalid credentials'
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        teachers.append(username)
        teacher_emails.update({
            username: email
        })
        teacher_schedules.update({
            username: {
        "08:00": {"Monday": "Math", "Tuesday": "", "Wednesday": "", "Thursday": "", "Friday": ""},
        "10:00": {"Monday": "", "Tuesday": "", "Wednesday": "", "Thursday": "", "Friday": ""},
        "12:00": {"Monday": "Research Meeting", "Tuesday": "Teachers' Council", "Wednesday": "", "Thursday": "", "Friday": ""},
        "14:00": {"Monday": "", "Tuesday": "", "Wednesday": "", "Thursday": "", "Friday": ""},
        "16:00": {"Monday": "", "Tuesday": "", "Wednesday": "Biology", "Thursday": "", "Friday": ""}
    }
        })
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/schedule/<teacher>')
def schedule(teacher):
    return render_template('schedule.html', teacher=teacher, schedule=teacher_schedules[teacher])

@app.route('/manage_requests')
def manage_requests():
    if 'username' not in session:
        return redirect(url_for('index'))
    
    relevant_requests = [req for req in requests if req['requested_teacher'] == session['username']]
    return render_template('manage_requests.html', requests=relevant_requests, teacher=session['username'])

@app.route('/handle_request/<req_id>', methods=['POST'])
def handle_request(req_id):
    request_id = req_id
    response = request.form["response"]
    
    schedule_req = [r for r in requests if r['request_id'] == request_id][0]

    if response == "Accept":
        teacher = session['username']
        day = schedule_req['day']
        time = schedule_req['time']
        teacher_schedules[teacher][time].update({day: schedule_req['request_title']})
    
    requests.remove(schedule_req)
        
    return redirect(url_for('manage_requests'))

@app.route('/request_slot', methods=['POST'])
def request_slot():
    req_teacher = request.form['teacher']
    day = request.form['day']
    slot = request.form['time']
    urgency = request.form['urgency']
    request_title = request.form['title']

    request_id = secrets.token_hex(8)

    request_info = {
        "request_id": request_id,
        "requesting_teacher": session["username"],
        "requested_teacher": req_teacher,
        "day": day,
        "time": slot,
        "urgency": urgency,
        "request_title": request_title
    }
    requests.append(request_info)

    # Send email notification
    send_email_notification(req_teacher, request_info)

    return redirect(url_for('schedule', teacher=req_teacher))

def send_email_notification(teacher, request_info):
    recipient_email = teacher_emails.get(teacher)
    if recipient_email:
        msg = Message("New Help Request for work",
                      recipients=[recipient_email])
        msg.body = (f"Hello {teacher},\n\n"
                    f"You have received a new request for {request_info['request_title']}.\n"
                    f"Details:\n"
                    f"Time: {request_info['time']}\n"
                    f"Day: {request_info['day']}\n"
                    f"Urgency: {request_info['urgency']}\n"
                    f"Requested by: {request_info['requesting_teacher']}\n\n"
                    "Please log in to your account to manage this request.\n\n"
                    "Best regards,\n"
                    "Your School Management System")
        mail.send(msg)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        # Check if the database is empty, and if so, populate it with initial data
        if User.query.count() == 0:
            initial_users = [
                {'username': 'Marija Trajanoska', 'email': 'macatrajanoska8@gmail.com', 'password': 'marija123'},
                {'username': 'Eli Zarlinova', 'email': 'elizarlinova02@gmail.com', 'password': 'eli123'},
                {'username': 'Teona Angelovska', 'email': 'teonaangelovska@gmail.com', 'password': 'teona123'}
            ]


            for user_data in initial_users:
                hashed_password = generate_password_hash(user_data['password'], method='pbkdf2:sha256')
                user = User(username=user_data['username'], email=user_data['email'], password=hashed_password)
                db.session.add(user)
            
            db.session.commit()

    app.run(debug=True)
