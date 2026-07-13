import os
from flask import Blueprint, render_template, request, redirect, url_for, current_app, flash
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_login import login_user, logout_user, login_required, current_user

from datetime import datetime
from app.models import User, Baby, Vaccination ,Growth, Sleep,Feeding,Medicine
from . import db

from flask import make_response
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO

import matplotlib.pyplot as plt

main = Blueprint("main", __name__)


@main.route("/")
def home():
    return render_template("home.html")

# ---------------- ABOUT ---------------- #
@main.route("/about")
def about():
    return render_template("about.html")
# ---------------- REGISTER ---------------- #

@main.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        hashed_password = generate_password_hash(password)

        user = User(
            name=name,
            email=email,
            password=hashed_password
        )

        db.session.add(user)
        db.session.commit()

        flash("Registration Successful! Please login.", "success")
        return redirect(url_for("main.login"))

    return render_template("register.html")


# ---------------- LOGIN ---------------- #

@main.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):

            login_user(user)

            return redirect(url_for("main.dashboard"))

        else:

            flash("Invalid Email or Password!", "danger")

    return render_template("login.html")

# ---------------- DASHBOARD ---------------- #

@main.route("/dashboard")
@login_required
def dashboard():

    vaccination_count = Vaccination.query.filter_by(user_id=current_user.id).count()
    feeding_count = Feeding.query.filter_by(user_id=current_user.id).count()
    sleep_count = Sleep.query.filter_by(user_id=current_user.id).count()
    growth_count = Growth.query.filter_by(user_id=current_user.id).count()
    medicine_count = Medicine.query.filter_by(user_id=current_user.id).count()

    vaccinations = Vaccination.query.filter_by(
        user_id=current_user.id
    ).order_by(Vaccination.vaccination_date).limit(5).all()

    medicines = Medicine.query.filter_by(
        user_id=current_user.id
    ).order_by(Medicine.medicine_date).limit(5).all()
    
    baby_count = Baby.query.filter_by(
    user_id=current_user.id
).count()
    return render_template(
        "dashboard.html",
        vaccinations=vaccinations,
        medicines=medicines,
        vaccination_count=vaccination_count,
        feeding_count=feeding_count,
        sleep_count=sleep_count,
        growth_count=growth_count,
        medicine_count=medicine_count,
        baby_count=baby_count,
    )
# ---------------- LOGIN REDIRECT ---------------- #

@main.route("/logout")
@login_required
def logout():

    logout_user()

    return redirect(url_for("main.login"))

# ---------------- BABY PROFILE ---------------- #
@main.route("/baby-profile", methods=["GET", "POST"])
@login_required
def baby_profile():

    # Save new baby first
    if request.method == "POST":

        photo = request.files["photo"]
        filename = None

        if photo and photo.filename:
            filename = secure_filename(photo.filename)

            upload_path = os.path.join(
                current_app.root_path,
                "static",
                "uploads",
                filename
            )

            photo.save(upload_path)

        baby = Baby(
            baby_name=request.form["baby_name"],
            dob=request.form["dob"],
            gender=request.form["gender"],
            blood_group=request.form["blood_group"],
            height=float(request.form["height"]) if request.form["height"] else None,
            weight=float(request.form["weight"]) if request.form["weight"] else None,
            photo=filename,
            parent_name=request.form["parent_name"],
            parent_phone=request.form["parent_phone"],
            user_id=current_user.id
        )

        db.session.add(baby)
        db.session.commit()

        flash("Baby profile added successfully!", "success")

        return redirect(url_for("main.baby_list"))

    # If Add Another Baby button is clicked, show empty form
    if request.args.get("new"):
        return render_template("baby_profile.html")

    # Otherwise show all babies
    babies = Baby.query.filter_by(user_id=current_user.id).all()

    return render_template(
        "baby_profile.html",
        babies=babies
    )

# ---------------- EDIT BABY  ---------------- #

@main.route("/baby/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_baby(id):

    baby = Baby.query.get_or_404(id)

    if request.method == "POST":

        # Upload new photo (optional)
        photo = request.files.get("photo")

        if photo and photo.filename:

            filename = secure_filename(photo.filename)

            upload_path = os.path.join(
                current_app.root_path,
                "static",
                "uploads",
                filename
            )

            photo.save(upload_path)

            baby.photo = filename

        # Update other details
        baby.baby_name = request.form["baby_name"]
        baby.dob = request.form["dob"]
        baby.gender = request.form["gender"]
        baby.blood_group = request.form["blood_group"]
        baby.height = float(request.form["height"]) if request.form["height"] else None
        baby.weight = float(request.form["weight"]) if request.form["weight"] else None
        baby.parent_name = request.form["parent_name"]
        baby.parent_phone = request.form["parent_phone"]

        db.session.commit()

        flash("Baby profile updated successfully!", "success")

        return redirect(url_for("main.view_baby", id=baby.id))

    return render_template(
        "edit_baby.html",
        baby=baby
    )

# ---------------- VIEW-BABY PROFILE  ---------------- #
@main.route("/view-baby/<int:id>")
@login_required
def view_baby(id):

    baby = Baby.query.get_or_404(id)

    dob = datetime.strptime(baby.dob, "%Y-%m-%d")
    today = datetime.today()

    years = today.year - dob.year
    months = today.month - dob.month

    if months < 0:
        years -= 1
        months += 12

    age = f"{years} Year(s) {months} Month(s)"

    return render_template(
        "view_baby.html",
        baby=baby,
        age=age
    )
# ---------------- BABY LIST  ---------------- #
@main.route("/baby-list")
@login_required
def baby_list():

    babies = Baby.query.filter_by(user_id=current_user.id).all()

    return render_template(
        "baby_list.html",
        babies=babies
    )
# ---------------- DELETE BABY  ---------------- #
@main.route("/baby/delete/<int:id>")
@login_required
def delete_baby(id):

    baby = Baby.query.get_or_404(id)

    db.session.delete(baby)
    db.session.commit()

    return "<h2>🗑️ Baby Profile Deleted Successfully!</h2>"

# ---------------- VACCINATION ---------------- #
@main.route("/vaccination", methods=["GET", "POST"])
@login_required
def vaccination():

    if request.method == "POST":

        vaccine = Vaccination(
            vaccine_name=request.form["vaccine_name"],
            vaccination_date=request.form["vaccination_date"],
            doctor_name=request.form["doctor_name"],
            notes=request.form["notes"],
            user_id=current_user.id
        )

        db.session.add(vaccine)
        db.session.commit()

        flash("Vaccination record added successfully!", "success")

        return redirect(url_for("main.vaccination"))

    search = request.args.get("search", "")

    vaccinations = Vaccination.query.filter(
        Vaccination.user_id == current_user.id,
        Vaccination.vaccine_name.contains(search)
    ).all()


    return render_template(
        "vaccination.html",
        vaccinations=vaccinations
    )
# ---------------- DELETE VACCINATION  ---------------- #
@main.route("/delete-vaccination/<int:id>")
@login_required
def delete_vaccination(id):

    vaccine = Vaccination.query.filter_by(
    id=id,
    user_id=current_user.id
).first_or_404()

    if vaccine.user_id != current_user.id:
        flash("Unauthorized access!", "danger")
        return redirect(url_for("main.vaccination"))

    db.session.delete(vaccine)
    db.session.commit()

    flash("Vaccination record deleted successfully!", "success")

    return redirect(url_for("main.vaccination"))
# ---------------- SLEEP  ---------------- #
@main.route("/sleep", methods=["GET", "POST"])
@login_required
def sleep():

    if request.method == "POST":

        record = Sleep(

            sleep_date=request.form["sleep_date"],

            sleep_start=request.form["sleep_start"],

            sleep_end=request.form["sleep_end"],

            duration=request.form["duration"],

            notes=request.form["notes"],

            user_id=current_user.id

        )

        db.session.add(record)
        db.session.commit()

        flash("Sleep record added successfully!", "success")

        return redirect(url_for("main.sleep"))

    search = request.args.get("search", "")

    sleep_records = Sleep.query.filter(
        Sleep.user_id == current_user.id,
        Sleep.notes.contains(search)
    ).all()

    return render_template(
        "sleep.html",
        sleep_records=sleep_records
    )
# ---------------- DELETE SLEEP  ---------------- #
@main.route("/delete-sleep/<int:id>")
@login_required
def delete_sleep(id):

    sleep = Sleep.query.filter_by(
        id=id,
        user_id=current_user.id
    ).first_or_404()

    db.session.delete(sleep)
    db.session.commit()

    flash("Sleep record deleted successfully!", "success")

    return redirect(url_for("main.sleep"))
# ---------------- SLEEP ---------------- #
@main.route("/growth", methods=["GET", "POST"])
@login_required
def growth():

    if request.method == "POST":

        record = Growth(

            record_date=request.form["record_date"],

            height=request.form["height"],

            weight=request.form["weight"],

            notes=request.form["notes"],

            user_id=current_user.id

        )

        db.session.add(record)
        db.session.commit()

        flash("Growth record added successfully!", "success")

        return redirect(url_for("main.growth"))

    search = request.args.get("search", "")

    growth_records = Growth.query.filter(
        Growth.user_id == current_user.id,
        Growth.record_date.contains(search)
    ).all()

    return render_template(
        "growth.html",
        growth_records=growth_records
    )
@main.route("/delete-growth/<int:id>")
@login_required
def delete_growth(id):

    growth = Growth.query.filter_by(
        id=id,
        user_id=current_user.id
    ).first_or_404()

    db.session.delete(growth)
    db.session.commit()

    flash("Growth record deleted successfully!", "success")

    return redirect(url_for("main.growth"))
# ---------------- FEEDING ---------------- #
@main.route("/feeding", methods=["GET", "POST"])
@login_required
def feeding():

    if request.method == "POST":

        record = Feeding(
            feeding_date=request.form["feeding_date"],
            feeding_time=request.form["feeding_time"],
            food_type=request.form["food_type"],
            quantity=request.form["quantity"],
            notes=request.form["notes"],
            user_id=current_user.id
        )

        db.session.add(record)
        db.session.commit()

        flash("Feeding record added successfully!", "success")

        return redirect(url_for("main.feeding"))

    search = request.args.get("search", "")

    feedings = Feeding.query.filter(
        Feeding.user_id == current_user.id,
        Feeding.food_type.contains(search)
    ).all()

    return render_template(
        "feeding.html",
        feedings=feedings
    )
@main.route("/delete-feeding/<int:id>")
@login_required
def delete_feeding(id):

    feeding = Feeding.query.filter_by(
        id=id,
        user_id=current_user.id
    ).first_or_404()

    db.session.delete(feeding)
    db.session.commit()

    flash("Feeding record deleted successfully!", "success")

    return redirect(url_for("main.feeding"))
# ---------------- MEDICINE ---------------- #
@main.route("/medicine", methods=["GET", "POST"])
@login_required
def medicine():

    if request.method == "POST":

        reminder = Medicine(
            medicine_name=request.form["medicine_name"],
            medicine_date=request.form["medicine_date"],
            medicine_time=request.form["medicine_time"],
            dosage=request.form["dosage"],
            notes=request.form["notes"],
            user_id=current_user.id
        )

        db.session.add(reminder)
        db.session.commit()

        flash("Medicine reminder added successfully!", "success")

        return redirect(url_for("main.medicine"))

    search = request.args.get("search", "")

    medicines = Medicine.query.filter(
        Medicine.user_id == current_user.id,
        Medicine.medicine_name.contains(search)
    ).all()
    
    return render_template(
        "medicine.html",
        medicines=medicines
    )
@main.route("/delete-medicine/<int:id>")
@login_required
def delete_medicine(id):

    medicine = Medicine.query.filter_by(
        id=id,
        user_id=current_user.id
    ).first_or_404()

    db.session.delete(medicine)
    db.session.commit()

    flash("Medicine reminder deleted successfully!", "success")

    return redirect(url_for("main.medicine"))
# ---------------- REPORTS ---------------- #
@main.route("/reports")
@login_required
def reports():

    growth_records = Growth.query.filter_by(user_id=current_user.id).all()

    vaccination_count = Vaccination.query.filter_by(user_id=current_user.id).count()
    feeding_count = Feeding.query.filter_by(user_id=current_user.id).count()
    sleep_count = Sleep.query.filter_by(user_id=current_user.id).count()
    growth_count = Growth.query.filter_by(user_id=current_user.id).count()
    medicine_count = Medicine.query.filter_by(user_id=current_user.id).count()

    if growth_records:

        dates = [g.record_date for g in growth_records]
        heights = [g.height for g in growth_records]
        weights = [g.weight for g in growth_records]

        # Height Chart
        plt.figure(figsize=(8,4))
        plt.plot(dates, heights, marker="o", linewidth=3)
        plt.title("Height Growth")
        plt.xlabel("Date")
        plt.ylabel("Height (cm)")
        plt.grid(True)
        plt.xticks(rotation=30)
        plt.tight_layout()

        plt.savefig(
            os.path.join(
                current_app.root_path,
                "static",
                "charts",
                "height_chart.png"
            )
        )
        plt.close()

        # Weight Chart
        plt.figure(figsize=(8,4))
        plt.plot(dates, weights, marker="o", linewidth=3)
        plt.title("Weight Growth")
        plt.xlabel("Date")
        plt.ylabel("Weight (kg)")
        plt.grid(True)
        plt.xticks(rotation=30)
        plt.tight_layout()

        plt.savefig(
            os.path.join(
                current_app.root_path,
                "static",
                "charts",
                "weight_chart.png"
            )
        )
        plt.close()

    return render_template(
        "reports.html",
        vaccination_count=vaccination_count,
        feeding_count=feeding_count,
        sleep_count=sleep_count,
        growth_count=growth_count,
        medicine_count=medicine_count
    )
# ---------------- CONTACTS ---------------- #
@main.route("/contact")
def contact():
    return render_template("contact.html")

# ---------------- DOWNLOAD PDF  ---------------- #
@main.route("/download-report/<int:id>")
@login_required
def download_report(id):

    baby = Baby.query.get_or_404(id)

    vaccinations = Vaccination.query.filter_by(user_id=current_user.id).all()
    growths = Growth.query.filter_by(user_id=current_user.id).all()
    feedings = Feeding.query.filter_by(user_id=current_user.id).all()
    sleeps = Sleep.query.filter_by(user_id=current_user.id).all()
    medicines = Medicine.query.filter_by(user_id=current_user.id).all()

    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer)

    styles = getSampleStyleSheet()

    story = []

    story.append(Paragraph("<b>BabyCare Health Report</b>", styles["Title"]))

    story.append(Paragraph(f"<b>Baby Name:</b> {baby.baby_name}", styles["Normal"]))
    story.append(Paragraph(f"<b>Date of Birth:</b> {baby.dob}", styles["Normal"]))
    story.append(Paragraph(f"<b>Gender:</b> {baby.gender}", styles["Normal"]))
    story.append(Paragraph(f"<b>Blood Group:</b> {baby.blood_group}", styles["Normal"]))
    story.append(Paragraph(f"<b>Height:</b> {baby.height} cm", styles["Normal"]))
    story.append(Paragraph(f"<b>Weight:</b> {baby.weight} kg", styles["Normal"]))
    story.append(Paragraph(f"<b>Parent:</b> {baby.parent_name}", styles["Normal"]))
    story.append(Paragraph(f"<b>Phone:</b> {baby.parent_phone}", styles["Normal"]))

    story.append(Paragraph("<br/><b>Vaccination Records</b>", styles["Heading2"]))

    for v in vaccinations:
        story.append(
            Paragraph(
                f"{v.vaccine_name} - {v.vaccination_date}",
                styles["Normal"]
            )
        )

    story.append(Paragraph("<br/><b>Growth Records</b>", styles["Heading2"]))

    for g in growths:
        story.append(
            Paragraph(
                f"{g.record_date} | Height: {g.height} cm | Weight: {g.weight} kg",
                styles["Normal"]
            )
        )

    story.append(Paragraph("<br/><b>Feeding Records</b>", styles["Heading2"]))

    for f in feedings:
        story.append(
            Paragraph(
                f"{f.feeding_date} {f.feeding_time} - {f.food_type} ({f.quantity})",
                styles["Normal"]
            )
        )

    story.append(Paragraph("<br/><b>Sleep Records</b>", styles["Heading2"]))

    for s in sleeps:
        story.append(
            Paragraph(
                f"{s.sleep_date} | {s.duration}",
                styles["Normal"]
            )
        )

    story.append(Paragraph("<br/><b>Medicine Records</b>", styles["Heading2"]))

    for m in medicines:
        story.append(
            Paragraph(
                f"{m.medicine_name} - {m.medicine_date} {m.medicine_time}",
                styles["Normal"]
            )
        )

    doc.build(story)

    pdf = buffer.getvalue()
    buffer.close()

    response = make_response(pdf)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = (
        f"attachment; filename={baby.baby_name}_Health_Report.pdf"
    )

    return response