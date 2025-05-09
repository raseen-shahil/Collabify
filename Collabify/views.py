from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db  # means from __init__.py import db
from flask_login import login_user, login_required, logout_user, current_user
from functools import wraps
from flask import abort


views = Blueprint("views", __name__)


def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if current_user.role != role:
                abort(403)
            return f(*args, **kwargs)

        return decorated_function

    return decorator


@views.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        role = request.form.get("role")

# Check for admin credentials first
        admin_email = "admin@gmail.com"  # Admin email
        user = User.query.filter_by(email=email).first()
        
        if user and email == admin_email:
            if check_password_hash(user.password, password):
                login_user(user, remember=True)
                flash("Logged in as Admin!", category="success")
                return redirect(url_for("admin.dashboard"))
            else:
                flash("Incorrect password for admin.", category="error")
        elif user:
            if check_password_hash(user.password, password):
                if user.role == role:  # Check if the user role matches the selected role
                    login_user(user, remember=True)
                    flash("Logged in successfully!", category="success")
                    if role == "Sponsor":
                        return redirect(url_for("sponsor.dashboard"))
                    elif role == "Influencer":
                        return redirect(url_for("influencer.dashboard"))
                else:
                    flash("Incorrect role selected. Please check your role.", category="error")
            else:
                flash("Incorrect password, try again.", category="error")
        else:
            flash("Email does not exist.", category="error")

    return render_template("login.html", user=current_user)


@views.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("views.login"))


@views.route("/sign-up", methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        email = request.form.get("email")
        name = request.form.get("firstName")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        role = request.form.get("role")
        niche = request.form.get("niche")

        user = User.query.filter_by(email=email).first()
        if user:
            flash("Email already exists.", category="error")
        elif len(email) < 4:
            flash("Email must be greater than 3 characters.", category="error")
        elif len(name) < 2:
            flash("First name must be greater than 1 character.", category="error")
        elif password1 != password2:
            flash("Passwords don't match.", category="error")
        elif len(password1) < 7:
            flash("Password must be at least 7 characters.", category="error")
        else:
            new_user = User(
                email=email,
                role=role,
                name=name,
                niche=niche,
                password=generate_password_hash(password1),
            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash("Account created!", category="success")
            return redirect(url_for("views.login"))

    return render_template("sign_up.html", user=current_user)
