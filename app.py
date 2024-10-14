from uuid import uuid4
from flask import Flask, request, render_template, flash
from pdfminer.pdfparser import PDFSyntaxError

from database import db
from timetable import get_patient_visits, generate_timetable, PatientVisit

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
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No uploaded file', 'danger')
        file = request.files['file']
        if file.filename == '':
            flash('No selected file', 'danger')
        try:
            visits = get_patient_visits(file.stream)
            if visits:
                visits.extend([
                    PatientVisit(lastname='Ho', firstname='Bao', dob='01/02/1920', age=None, procedure='Colonoscopy'),
                    PatientVisit(lastname='Doe', firstname='Jane', dob='02/05/1992', age=None, procedure='Gastroscopy'),
                    PatientVisit(lastname='Bio', firstname='Bla', dob='29/03/2005', age=None, procedure='Gastroscopy + Colonoscopy'),
                    PatientVisit(lastname='Lilo', firstname='Bolta', dob='22/03/2010', age=None, procedure='Colonoscopy'),
                    PatientVisit(lastname='Bah', firstname='Baaa', dob='03/11/2007', age=None, procedure='Gastroscopy + Colonoscopy'),
                    PatientVisit(lastname='Birda', firstname='Bora', dob='15/12/1998', age=None, procedure='Colonoscopy'),
                    PatientVisit(lastname='Heho', firstname='Baobao', dob='28/09/1984', age=None, procedure='Colonoscopy'),
                    PatientVisit(lastname='Zog', firstname='Zag', dob='16/04/1987', age=None, procedure='Gastroscopy'),
                    PatientVisit(lastname='Mao', firstname='Hoja', dob='30/08/2012', age=None, procedure='Gastroscopy + Colonoscopy'),
                ])
                table = generate_timetable(visits)
            else:
                flash('The uploaded file does not contain data in the correct format', 'danger')
        except PDFSyntaxError:
            flash('The uploaded file is not a valid PDF file', 'danger')
        except Exception as e:
            flash(f'{type(e).__name__}: {e}', 'danger')
    return render_template('index.html', table=table)


if __name__ == '__main__':
    app.run()

