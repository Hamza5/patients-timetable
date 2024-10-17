import re
import pdfplumber
from dataclasses import dataclass
from datetime import datetime, timedelta, date

from database import ProcedureSettings, GeneralSettings

PATIENT_INFO_RE = re.compile(
    r'(?P<lastname>.+?),\s*(?P<firstname>.+?)\s+M\w+\s+\((?P<sex>\w)\)\nDOB:\s*(?P<dob>\d+/\d+/\d+)\s*\((?P<age>\d+)', re.MULTILINE
)


def normalize_procedure(procedure):
    procedure = procedure.strip().title()
    if 'Gastroscopy' in procedure and 'Colonoscopy' in procedure:
        return 'Gastroscopy + Colonoscopy'
    elif procedure.startswith('Gastroscopy'):
        return 'Gastroscopy'
    elif procedure.startswith('Colonoscopy'):
        return 'Colonoscopy'
    return procedure


@dataclass
class PatientVisit:
    lastname: str
    firstname: str
    sex: str
    dob: str
    age: int | None
    procedure: str

    def get_age(self) -> int:
        return self.age or (date.today() - datetime.strptime(self.dob, '%d/%m/%Y').date()) // timedelta(days=365.25)

    def __repr__(self):
        representation = f'{self.__class__.__name__}('
        for field in self.__dataclass_fields__:
            if field == 'age':
                representation += f'{field}={self.get_age()}, '
            else:
                representation += f'{field}={getattr(self, field)}, '
        return representation[:-2] + ')'


def get_title_info(pdf: pdfplumber.PDF):
    title = pdf.pages[0].extract_text_simple().splitlines()[0]
    return [x.strip() for x in title.split('-')[::2]]


def get_patient_visits(pdf_file):
    with pdfplumber.open(pdf_file) as pdf:
        patient_visits = []
        for page in pdf.pages:
            table = page.extract_table()
            if not table:
                continue
            for row in table:
                procedure = (row[3] or '\n').splitlines()[0]
                re_result = PATIENT_INFO_RE.match(row[1] or '')
                if re_result:
                    patient_visits.append(PatientVisit(
                        lastname=re_result.group('lastname'),
                        firstname=re_result.group('firstname'),
                        sex=re_result.group('sex'),
                        dob=re_result.group('dob'),
                        age=int(re_result.group('age')) if re_result.group('age').isnumeric() else None,
                        procedure=normalize_procedure(procedure),
                    ))
        return patient_visits, get_title_info(pdf)


def round_time(dt=None, round_to=60):
    """Round a datetime object to any timelapse in seconds
    :param dt : datetime.datetime object, default now.
    :param round_to : Closest number of seconds to round to, default 1 minute.
    Author: Thierry Husson 2012 - Use it as you want but don't blame me.
    https://stackoverflow.com/questions/3463930/how-to-round-the-minute-of-a-datetime-object/10854034#10854034
    """
    if dt is None:
        dt = datetime.now()
    if round_to <= 0:
        return dt
    seconds = (dt.replace(tzinfo=None) - dt.min).seconds
    rounding = (seconds + round_to / 2) // round_to * round_to
    return dt + timedelta(0, rounding-seconds, -dt.microsecond)


def generate_timetable(patients_visits: list[PatientVisit]):
    start_time = datetime.strptime(GeneralSettings.get(GeneralSettings.key == 'First patient time').value, '%H:%M')
    time_unit = timedelta(minutes=int(GeneralSettings.get(GeneralSettings.key == 'Time unit').value))
    launch_duration = timedelta(minutes=int(GeneralSettings.get(GeneralSettings.key == 'Launch duration').value))
    launch_min_time = datetime.strptime(GeneralSettings.get(GeneralSettings.key == 'Launch min time').value, '%H:%M')
    intersession_break = timedelta(minutes=int(GeneralSettings.get(GeneralSettings.key == 'Inter-session break').value))
    timetable = []
    for visit in patients_visits:
        rules = ProcedureSettings.select().where(
            (ProcedureSettings.procedure == visit.procedure) &
            (ProcedureSettings.minAge.is_null() | (ProcedureSettings.minAge <= visit.get_age())) &
            (ProcedureSettings.maxAge.is_null() | (ProcedureSettings.maxAge >= visit.get_age()))
        )
        if not rules:
            rules = ProcedureSettings.select().where(ProcedureSettings.procedure == 'Gastroscopy')
        start_time = round_time(start_time, time_unit.seconds)
        end_time = round_time(start_time + timedelta(minutes=rules[0].duration) + intersession_break, time_unit.seconds)
        timetable_entry = {
            'lastname': visit.lastname,
            'firstname': visit.firstname,
            'sex': visit.sex,
            'dob': visit.dob,
            'age': visit.get_age(),
            'procedure': visit.procedure,
            'start_time': start_time.strftime('%H:%M'),
            'end_time': end_time.strftime('%H:%M'),
        }
        timetable.append(timetable_entry)
        start_time += end_time - start_time
        if start_time >= launch_min_time and not list(filter(lambda x: x['procedure'] == 'Launch break', timetable)):
            timetable.append({
                'lastname': '',
                'firstname': '',
                'sex': '',
                'dob': '',
                'age': '',
                'procedure': 'Launch break',
                'start_time': start_time.strftime('%H:%M'),
                'end_time': (start_time + launch_duration).strftime('%H:%M'),
            })
            start_time += launch_duration
    return timetable
