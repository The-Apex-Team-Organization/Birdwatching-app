from functools import wraps
from flask import url_for, redirect, session, flash
from Birdwatching.utils.databases import get_post


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("You must be logged in to access this page.", "danger")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function


def is_allowed_post(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        post = get_post(kwargs["post_id"])
        if session["user_role"] == "admin" or post["user_id"] == session["user_id"]:
            return f(*args, **kwargs)
        flash('You are not allowed to be there!')
        return redirect(url_for('main.index'))

    return decorated_function


def is_allowed_user(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session["user_role"] == "admin" or kwargs["id"] == session["user_id"]:
            return f(*args, **kwargs)
        flash('You are not allowed to be there!')
        return redirect(url_for('main.index'))
    return decorated_function


def is_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session["user_role"] == "admin":
            return f(*args, **kwargs)
        flash('You are not allowed to be there!')
        return redirect(url_for('main.index'))
    return decorated_function
