from flask import Blueprint, render_template
from Birdwatching.utils.decorators import login_required
from Birdwatching.utils.databases import get_posts_users


main_bp = Blueprint("main", __name__)


@main_bp.route('/')
@login_required
def index():
    posts = get_posts_users()
    return render_template('index.html', posts=posts)
