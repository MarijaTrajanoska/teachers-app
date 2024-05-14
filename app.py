from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import secrets


app = Flask(__name__)
app.secret_key = secrets.token_hex(8)  # Needed for session management


teachers = ["John Doe", "Jane Smith"]
# Sample data for teachers and their schedules
teacher_schedules = {
    "John Doe": {
        "Monday": {"08:00": "Math", "10:00": "", "12:00": "Research Meeting", "14:00": "", "16:00": ""},
        "Tuesday": {"08:00": "", "10:00": "", "12:00": "Teachers' Council", "14:00": "", "16:00": ""},
        "Wednesday": {"08:00": "", "10:00": "", "12:00": "", "14:00": "", "16:00": "Biology"},
        "Thursday": {"08:00": "", "10:00": "", "12:00": "", "14:00": "", "16:00": ""},
        "Friday": {"08:00": "", "10:00": "", "12:00": "", "14:00": "", "16:00": ""}
    },
    "Jane Smith": {
        "Monday": {"08:00": "", "10:00": "", "12:00": "", "14:00": "", "16:00": ""},
        "Tuesday": {"08:00": "", "10:00": "", "12:00": "Teachers' Council", "14:00": "", "16:00": ""},
        "Wednesday": {"08:00": "Physics", "10:00": "", "12:00": "", "14:00": "", "16:00": ""},
        "Thursday": {"08:00": "", "10:00": "", "12:00": "", "14:00": "", "16:00": ""},
        "Friday": {"08:00": "", "10:00": "", "12:00": "", "14:00": "Grades administrative", "16:00": ""}
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
        teacher_schedules[teacher][day].update({time: schedule_req['request_title']})
    
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

    request_info = {"request_id": request_id,
                     "requesting_teacher": session["teacher_name"],
                      "requested_teacher": req_teacher,
                      "day": day,
                      "time": slot, 
                       "urgency": urgency,
                       "request_title": request_title}
    requests.append(request_info)
    return redirect(url_for('schedule', teacher=req_teacher))

if __name__ == '__main__':
    app.run(debug=True)