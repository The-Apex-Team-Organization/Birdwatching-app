import os
import datetime
import boto3
from werkzeug.utils import secure_filename
from flask import (Blueprint, render_template, request, session,
                   url_for, redirect, flash, current_app)
from Birdwatching.utils.databases import post_sql, get_post
from Birdwatching.utils.decorators import is_allowed_post, login_required
from Birdwatching.utils.middlewares import upload_to_s3


posts_bp = Blueprint('posts', __name__)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() \
        in current_app.config["ALLOWED_EXTENSIONS"]


@posts_bp.route('/<int:post_id>/edit', methods=('GET', 'POST'))
@login_required
@is_allowed_post
def edit(post_id):
    post = get_post(post_id)

    if request.method == 'POST':
        location = request.form.get('location', '').strip()
        file = request.files.get('image')

        if not location:
            flash('location is required!')
            return render_template('posts/edit.html', post=post)

        filename = None
        if file and file.filename:
            if not allowed_file(file.filename):
                flash('Invalid file type!')
                return render_template('posts/edit.html', post=post)
            filename = secure_filename(
                f"{datetime.datetime.now()}_{file.filename}")
            try:
                upload_to_s3(file, filename)
            except Exception as e:
                print(f'Error saving file: {e}')
                return render_template('posts/edit.html', post=post)

        try:
            if filename:
                post_sql('UPDATE posts SET location = :location, image_path = :image_path WHERE id = :id',
                         {"location": location, "image_path": filename, "id": post_id})
            else:
                post_sql(
                    'UPDATE posts SET location = :location WHERE id = :id',
                    {"location": location, "id": post_id})

            flash('Post updated successfully!')
            return redirect(url_for('main.index'))

        except Exception as e:
            print(f'Database error: {e}')
            return render_template('posts/edit.html', post=post)

    return render_template('posts/edit.html', post=post)


@posts_bp.route('/<int:post_id>/delete', methods=('POST',))
@login_required
@is_allowed_post
def delete(post_id):
    post_sql(f'DELETE FROM posts WHERE id = :id',
             {"id": post_id})

    flash("Post was successfully deleted!", "info")
    return redirect(url_for('main.index'))


@posts_bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        location = request.form['location']
        file = request.files.get('image')

        if not location or not file:
            flash('Location and image are required!')
        elif not allowed_file(file.filename):
            flash('Invalid file type!')
        else:
            filename = secure_filename(
                f"{datetime.datetime.now()}_{file.filename}")
            upload_to_s3(file, filename)
            post_sql(
                'INSERT INTO posts (user_id, location, image_path) VALUES (:user_id, :location, :image_path)', {
                    "user_id": session["user_id"], "location": location, "image_path": filename}

            )
        return redirect(url_for('main.index'))

    return render_template('posts/create.html')
