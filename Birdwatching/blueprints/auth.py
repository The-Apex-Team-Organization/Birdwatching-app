from flask import (Blueprint, render_template, request,
                   redirect, session, flash, url_for)
from werkzeug.security import generate_password_hash, check_password_hash
from Birdwatching.utils.decorators import login_required
from Birdwatching.utils.databases import get_user_by_username, insert_user

auth_bp = Blueprint('auth', __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        hashed_pw = generate_password_hash(password)

        if get_user_by_username(username):
            flash("User already exists")
            return render_template("auth/register.html")
        insert_user(username, hashed_pw)

        flash("Account created! You can now log in.", "success")
        return redirect(url_for("auth.login"))
    return render_template("auth/register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = get_user_by_username(username)

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["user_role"] = user["user_role"]
            flash("Login successful!", "success")
            return redirect(url_for("users.home"))

        flash("Invalid credentials", "danger")

    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    session.clear()
    flash("Logged out.", "info")
    return redirect(url_for("users.home"))
