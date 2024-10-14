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


class GeneralSettings(BaseMode):
    key = CharField()
    value = CharField()


def init_db():
    db.connect()
    models = [ProcedureSettings, GeneralSettings]
    db.drop_tables(models, safe=True)
    db.create_tables(models)
    with db.atomic():
        ProcedureSettings.create(procedure='Gastroscopy', duration=20)
        ProcedureSettings.create(procedure='Colonoscopy', maxAge=39, duration=30)
        ProcedureSettings.create(procedure='Colonoscopy', minAge=40, maxAge=75, duration=35)
        ProcedureSettings.create(procedure='Colonoscopy', minAge=76, duration=50)
        ProcedureSettings.create(procedure='Gastroscopy + Colonoscopy', maxAge=39, duration=40)
        ProcedureSettings.create(procedure='Gastroscopy + Colonoscopy', minAge=40, maxAge=75, duration=45)
        ProcedureSettings.create(procedure='Gastroscopy + Colonoscopy', minAge=76, duration=50)
        GeneralSettings.create(key='First patient time', value='07:00')
        GeneralSettings.create(key='Launch duration', value='40')
        GeneralSettings.create(key='Launch min time', value='12:30')
        GeneralSettings.create(key='Time unit', value='15')
        GeneralSettings.create(key='Inter-session break', value='10')
    db.close()


if __name__ == '__main__':
    init_db()
