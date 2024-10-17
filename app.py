from uuid import uuid4
from flask import Flask, request, render_template, flash
from pdfminer.pdfparser import PDFSyntaxError

from database import db
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
            visits, [title, doctor] = get_patient_visits(file.stream)
            if visits:
                table = generate_timetable(visits)
            else:
                flash('The uploaded file does not contain data in the correct format', 'danger')
        except PDFSyntaxError:
            flash('The uploaded file is not a valid PDF file', 'danger')
        except Exception as e:
            flash(f'{type(e).__name__}: {e}', 'danger')
    return render_template('index.html', table=table, title=title, doctor=doctor)


if __name__ == '__main__':
    app.run()

