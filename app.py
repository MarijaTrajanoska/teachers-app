from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import secrets
from flask_mail import Mail, Message

app = Flask(__name__)
app.secret_key = secrets.token_hex(8)  # Needed for session management

# Configure Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Use your mail server
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'teachersapp2024@gmail.com'  # Your email
app.config['MAIL_PASSWORD'] = 'ppeeaywbxlrcplzt'  # Your email password
app.config['MAIL_DEFAULT_SENDER'] = 'teachersapp2024@gmail.com'

mail = Mail(app)

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
    if 'teacher_name' not in session:
        return render_template('login.html')
    return render_template("index.html", teachers=teachers)

@app.route('/login_action', methods=['POST'])
def login_action():
    teacher_name = request.form['teacher_name']
    if teacher_name in teachers:
        session['teacher_name'] = teacher_name
        return redirect(url_for('index'))
    return 'Teacher not found'

@app.route('/logout')
def logout():
    session.pop('teacher_name', None)
    return redirect(url_for('index'))

@app.route('/schedule/<teacher>')
def schedule(teacher):
    return render_template('schedule.html', teacher=teacher, schedule=teacher_schedules[teacher])

@app.route('/manage_requests')
def manage_requests():
    if 'teacher_name' not in session:
        return redirect(url_for('index'))
    
    relevant_requests = [req for req in requests if req['requested_teacher'] == session['teacher_name']]
    return render_template('manage_requests.html', requests=relevant_requests, teacher=session['teacher_name'])

@app.route('/handle_request/<req_id>', methods=['POST'])
def handle_request(req_id):
    request_id = req_id
    response = request.form["response"]
    
    schedule_req = [r for r in requests if r['request_id'] == request_id][0]

    if response == "Accept":
        teacher = session['teacher_name']
        day = schedule_req['day']
        time = schedule_req['time']
        teacher_schedules[teacher][time].update({day: schedule_req['request_title']})
    
    requests.remove(schedule_req)
        
    # Here you would update the request status in your data structure
    # Redirect to manage_requests or another appropriate page
    return redirect(url_for('manage_requests'))

@app.route('/request_slot', methods=['POST'])
def request_slot():
    req_teacher = request.form['teacher']
    day = request.form['day']
    slot = request.form['time']
    urgency = request.form['urgency']  # This field should be added to the form in the HTML
    request_title = request.form['title']

    request_id = secrets.token_hex(8)

    request_info = {
        "request_id": request_id,
        "requesting_teacher": session["teacher_name"],
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
    app.run(debug=True)
