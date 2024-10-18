from peewee import *

db = SqliteDatabase('db.sqlite3')


class BaseMode(Model):

    class Meta:
        database = db


class ProcedureSettings(BaseMode):
    procedure = CharField()
    minAge = IntegerField(null=True)
    maxAge = IntegerField(null=True)
    duration = IntegerField()
    doctor = CharField()


class GeneralSettings(BaseMode):
    key = CharField()
    value = CharField()


def get_doctor_names():
    results = ProcedureSettings.select(ProcedureSettings.doctor).distinct()
    return [r.doctor for r in results]


def init_db():
    db.connect()
    models = [ProcedureSettings, GeneralSettings]
    db.drop_tables(models, safe=True)
    db.create_tables(models)
    with db.atomic():
        ProcedureSettings.create(procedure='Gastroscopy', duration=20, doctor='Nagree')
        ProcedureSettings.create(procedure='Colonoscopy', maxAge=39, duration=30, doctor='Nagree')
        ProcedureSettings.create(procedure='Colonoscopy', minAge=40, maxAge=75, duration=35, doctor='Nagree')
        ProcedureSettings.create(procedure='Colonoscopy', minAge=76, duration=50, doctor='Nagree')
        ProcedureSettings.create(procedure='Gastroscopy + Colonoscopy', maxAge=39, duration=40, doctor='Nagree')
        ProcedureSettings.create(procedure='Gastroscopy + Colonoscopy', minAge=40, maxAge=75, duration=45, doctor='Nagree')
        ProcedureSettings.create(procedure='Gastroscopy + Colonoscopy', minAge=76, duration=50, doctor='Nagree')

        ProcedureSettings.create(procedure='Gastroscopy', duration=25, doctor='Pulusu')
        ProcedureSettings.create(procedure='Colonoscopy', maxAge=39, duration=45, doctor='Pulusu')
        ProcedureSettings.create(procedure='Colonoscopy', minAge=40, maxAge=75, duration=50, doctor='Pulusu')
        ProcedureSettings.create(procedure='Colonoscopy', minAge=76, duration=55, doctor='Pulusu')
        ProcedureSettings.create(procedure='Gastroscopy + Colonoscopy', maxAge=39, duration=60, doctor='Pulusu')
        ProcedureSettings.create(procedure='Gastroscopy + Colonoscopy', minAge=40, maxAge=75, duration=65, doctor='Pulusu')
        ProcedureSettings.create(procedure='Gastroscopy + Colonoscopy', minAge=76, duration=70, doctor='Pulusu')

        for doctor in ['Broughton', 'Nasa']:
            ProcedureSettings.create(procedure='Gastroscopy', duration=15, doctor=doctor)
            ProcedureSettings.create(procedure='Colonoscopy', maxAge=39, duration=25, doctor=doctor)
            ProcedureSettings.create(procedure='Colonoscopy', minAge=40, maxAge=75, duration=30, doctor=doctor)
            ProcedureSettings.create(procedure='Colonoscopy', minAge=76, duration=35, doctor=doctor)
            ProcedureSettings.create(procedure='Gastroscopy + Colonoscopy', maxAge=39, duration=30, doctor=doctor)
            ProcedureSettings.create(procedure='Gastroscopy + Colonoscopy', minAge=40, maxAge=75, duration=35, doctor=doctor)
            ProcedureSettings.create(procedure='Gastroscopy + Colonoscopy', minAge=76, duration=40, doctor=doctor)

        ProcedureSettings.create(procedure='Gastroscopy', duration=20, doctor='Mcelholm')
        ProcedureSettings.create(procedure='Colonoscopy', maxAge=39, duration=30, doctor='Mcelholm')
        ProcedureSettings.create(procedure='Colonoscopy', minAge=40, maxAge=75, duration=35, doctor='Mcelholm')
        ProcedureSettings.create(procedure='Colonoscopy', minAge=76, duration=45, doctor='Mcelholm')
        ProcedureSettings.create(procedure='Gastroscopy + Colonoscopy', maxAge=39, duration=40, doctor='Mcelholm')
        ProcedureSettings.create(procedure='Gastroscopy + Colonoscopy', minAge=40, maxAge=75, duration=50, doctor='Mcelholm')
        ProcedureSettings.create(procedure='Gastroscopy + Colonoscopy', minAge=76, duration=55, doctor='Mcelholm')

        GeneralSettings.create(key='First patient time', value='07:00')
        GeneralSettings.create(key='Launch duration', value='40')
        GeneralSettings.create(key='Launch min time', value='12:30')
        GeneralSettings.create(key='Time unit', value='15')
        GeneralSettings.create(key='Inter-session break', value='0')
    db.close()


if __name__ == '__main__':
    init_db()
