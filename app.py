from flask import Flask, render_template, request, redirect, url_for, jsonify

app = Flask(__name__)

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
    return render_template('index.html', teachers=teachers)


@app.route('/schedule/<teacher>')
def schedule(teacher):
    return render_template('schedule.html', teacher=teacher, schedule=teacher_schedules.get(teacher, {}))


@app.route('/request', methods=['POST'])
def request_slot():
    if request.method == 'POST':
        teacher = request.form['teacher']
        day = request.form['day']
        slot = request.form['slot']
        request_info = {'teacher': teacher, 'day': day, 'slot': slot}
        requests.append(request_info)
        notify_other_teacher(teacher, day, slot)
        return redirect(url_for('index'))


@app.route('/accept_request', methods=['POST'])
def accept_request():
    if request.method == 'POST':
        teacher = request.form['teacher']
        day = request.form['day']
        slot = request.form['slot']
        teacher_schedules[teacher][day][slot] = "Project"
        return jsonify({'message': 'Request accepted.'})


def notify_other_teacher(teacher, day, slot):
    # Here you can implement the notification mechanism, for simplicity we just print the notification
    print(f"Notification sent to other teacher: {teacher} on {day} at {slot}.")


if __name__ == '__main__':
    app.run(debug=True)
