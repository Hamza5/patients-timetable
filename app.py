from uuid import uuid4
from flask import Flask, request, render_template, flash
from pdfminer.pdfparser import PDFSyntaxError

from database import db, get_doctor_names
from timetable import get_patient_visits, generate_timetable

app = Flask(__name__)
app.secret_key = str(uuid4())


@app.before_request
def before_request():
    db.connect()


@app.after_request
def after_request(response):
    db.close()
    return response


@app.route('/', methods=['GET', 'POST'])
def index():
    table = None
    title = None
    doctor = None
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No uploaded file', 'danger')
        file = request.files['file']
        if file.filename == '':
            flash('No selected file', 'danger')
        try:
            visits, info = get_patient_visits(file.stream)
            if visits:
                [title, doctor] = info
                if request.form.get('doctor'):
                    doctor = request.form.get('doctor')
                table = generate_timetable(visits, doctor)
            else:
                flash('The uploaded file does not contain data in the correct format', 'danger')
        except PDFSyntaxError:
            flash('The uploaded file is not a valid PDF file', 'danger')
        except Exception as e:
            flash(f'{type(e).__name__}: {e}', 'danger')
            import traceback
            traceback.print_exception(e)
    return render_template('index.html', table=table, title=title, doctor=doctor, doctor_names=get_doctor_names())


if __name__ == '__main__':
    app.run()

