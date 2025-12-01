import hashlib
import re
from flask import Blueprint, render_template, request, url_for, redirect, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from Birdwatching.utils.databases import post_sql, get_user, get_ip_address, get_user_posts

from Birdwatching.utils.decorators import login_required, is_allowed_user

users_bp = Blueprint("users", __name__)


@users_bp.route('/users/<int:id>/delete', methods=('POST',))
@login_required
@is_allowed_user
def delete(id):
    post_sql(f'DELETE FROM users WHERE id = :id', {"id": id})
    flash("User was successfully deleted!", "info")
    return redirect(url_for('main.index'))


@users_bp.route("/users/<int:id>/edit", methods=("GET", "POST"))
@login_required
@is_allowed_user
def edit(id):
    user = get_user(id)
    if user is None:
        flash("This user doesnt exist")
        return redirect(url_for('users.home'))

    if request.method == "POST":
        if session["user_role"] == "admin":
            new_password = request.form["new_password"]
            if new_password != "":
                hashed_pw = generate_password_hash(new_password)
                post_sql("UPDATE users SET user_role = :user_role, password = :password WHERE id = :id",
                         {"user_role": request.form["role"], "password": hashed_pw, "id": user["id"]})
            else:
                post_sql("UPDATE users SET user_role = :user_role WHERE id = :id",
                         {"user_role": request.form["role"], "id": user["id"]})
            flash("Succesfully updated")
            return redirect(url_for("users.home"))

        elif session["user_role"] == "user":
            new_password = request.form["new_password"]
            old_password = request.form["old_password"]


            if user and check_password_hash(user["password"], old_password):
                hashed_pw = generate_password_hash(new_password)

                post_sql("UPDATE users SET password = :password WHERE id = :id",
                         {"password": hashed_pw, "id": user["id"]})
                flash("Succesfully updated")
                return redirect(url_for("users.home"))
            else:
                flash("Wrong password")


    return render_template('users/edit.html', user=user)


@users_bp.route("/home")
@login_required
def home():
    if "user_id" in session:
        return render_template("users/home.html",
                               username=session["username"],
                               posts=get_user_posts(session["user_id"]))
    return render_template("users/home.html", username=None)


@users_bp.route('/report', methods=("GET", "POST"))
@login_required
def report():
    if request.method == "POST":
        ip_address = request.form["ip_address"]
        if ip_address:
            ip_address_validate = re.search(
                r"^((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)\.?\b){4}$", ip_address)
            if ip_address_validate:
                ip_address_hashed = hashlib.sha256(
                    bytes(ip_address_validate.string.encode())).hexdigest()
                isExist = get_ip_address(ip_address_hashed)
                if not isExist:
                    post_sql(
                        "INSERT INTO black_list (ip_address) VALUES (:ip_address)",
                        {"ip_address": ip_address_hashed})
                    flash("You successfully reported ip address")
                    return redirect(url_for('main.index'))
                else:
                    flash("Ip address already in black list")
            else:
                flash("Enter valid ip address")
        else:
            flash("Enter ip address")

    return render_template('users/report.html')
