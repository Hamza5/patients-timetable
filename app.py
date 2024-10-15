from collections import defaultdict
from uuid import uuid4
from flask import Flask, request, render_template, flash
from pdfminer.pdfparser import PDFSyntaxError

from database import db
from timetable import get_patient_visits, generate_timetable

app = Flask(__name__)
app.secret_key = str(uuid4())


@app.template_filter('procedure_badge_color')
def procedure_badge_color(procedure):
    mapping = defaultdict(lambda: 'bg-orange-lt')
    mapping.update({
        'Gastroscopy': 'bg-blue-lt',
        'Colonoscopy': 'bg-green-lt',
        'Gastroscopy + Colonoscopy': 'bg-cyan-lt'
    })
    return mapping[procedure]


app.jinja_env.filters['procedure_badge_color'] = procedure_badge_color


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

