from . import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    email = db.Column(db.String(120), unique=True, nullable=False)

    password = db.Column(db.String(255), nullable=False)

class Baby(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    baby_name = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.String(20), nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    blood_group = db.Column(db.String(10))
    height = db.Column(db.Float)
    weight = db.Column(db.Float)
    photo = db.Column(db.String(200))
    parent_name = db.Column(db.String(100))
    parent_phone = db.Column(db.String(20))

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
class Vaccination(db.Model):

        id = db.Column(db.Integer, primary_key=True)

        vaccine_name = db.Column(db.String(100), nullable=False)

        vaccination_date = db.Column(db.String(20), nullable=False)

        doctor_name = db.Column(db.String(100))

        notes = db.Column(db.Text)

        user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
class Feeding(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    feeding_date = db.Column(db.String(20), nullable=False)

    feeding_time = db.Column(db.String(20), nullable=False)

    food_type = db.Column(db.String(100), nullable=False)

    quantity = db.Column(db.String(50))

    notes = db.Column(db.Text)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
class Sleep(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    sleep_date = db.Column(db.String(20), nullable=False)

    sleep_start = db.Column(db.String(20), nullable=False)

    sleep_end = db.Column(db.String(20), nullable=False)

    duration = db.Column(db.String(20))

    notes = db.Column(db.Text)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

class Growth(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    record_date = db.Column(db.String(20), nullable=False)

    height = db.Column(db.Float, nullable=False)

    weight = db.Column(db.Float, nullable=False)

    notes = db.Column(db.Text)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
class Medicine(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    medicine_name = db.Column(db.String(100), nullable=False)

    medicine_date = db.Column(db.String(20), nullable=False)

    medicine_time = db.Column(db.String(20), nullable=False)

    dosage = db.Column(db.String(50), nullable=False)

    notes = db.Column(db.Text)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))