from flask import Blueprint, render_template
from Birdwatching.utils.databases import get_users
from Birdwatching.utils.decorators import is_admin, login_required

admin_bp = Blueprint("admin", __name__)


@admin_bp.route('/admin', methods=("GET", "POST"))
@login_required
@is_admin
def admin():
    users = get_users()
    return render_template('admin/admin.html', users=users)
