from flask import Flask, request
from database import db
from timetable import get_patient_visits, generate_timetable, PatientVisit

app = Flask(__name__)


@app.before_request
def before_request():
    db.connect()


@app.after_request
def after_request(response):
    db.close()
    return response


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'No file part', 400
        file = request.files['file']
        if file.filename == '':
            return 'No selected file', 400
        visits = get_patient_visits(file.stream)
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
        return generate_timetable(visits)
    else:
        return '''
    <!doctype html>
    <title>Upload a PDF file</title>
    <h1>Upload a PDF file</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''


if __name__ == '__main__':
    app.run()

