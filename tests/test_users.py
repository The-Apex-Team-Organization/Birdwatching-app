from Birdwatching.utils.databases import insert_user, get_user_by_username, get_user, post_sql
from werkzeug.security import generate_password_hash, check_password_hash
import hashlib
from Birdwatching.utils.databases import post_sql, get_ip_address

def test_delete_user(client, app):
    with app.app_context():
        password = generate_password_hash('password')
        insert_user('user1', password)
        user = get_user_by_username('user1')
        user_id = user['id']

    client.post('/auth/login', data={
        'username': 'user1',
        'password': 'password',
    })
    
    with client.session_transaction() as session:
        assert 'user_id' in session
        assert 'username' in session
        assert 'user_role' in session
        
    response = client.post(f'/users/{user_id}/delete', follow_redirects=True)
    assert response.status_code == 200
    
    with app.app_context():
        deleted_user = get_user(user_id)
        assert deleted_user is None

def test_edit_user_none(client, app):
    with client.session_transaction() as session:
        session['user_id'] = 1
        session['user_role'] = 'admin'
        session["username"] = "user1"

    response = client.get('/users/1/edit', follow_redirects=True)
    assert response.status_code == 500

def test_edit_admin_with_new_password(client, app):
    with app.app_context():
        post_sql("INSERT INTO users (username, password, user_role) VALUES (:username, :password, :role)",
                     {"username": "user1", "password": generate_password_hash("password"), "role": "user"})
        user = get_user_by_username("user1")

    with client.session_transaction() as session:
        session["user_id"] = user["id"]
        session["user_role"] = "admin"
        session["username"] = "user1"

    response = client.post(
        f"/users/{user['id']}/edit",
        data={"new_password": "newpassword", "role": "somerole"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Succesfully updated" in response.data

    with app.app_context():
        updated_user = get_user(user["id"])
        assert updated_user["user_role"] == "somerole"


def test_edit_admin_without_password(client, app):
    with app.app_context():
        post_sql("INSERT INTO users (username, password, user_role) VALUES (:username, :password, :role)",
                     {"username": "user1", "password": generate_password_hash("password"), "role": "user"})
        user = get_user_by_username("user1")

    with client.session_transaction() as session:
        session["user_id"] = user["id"]
        session["user_role"] = "admin"
        session["username"] = "user1"

    response = client.post(
        f"/users/{user['id']}/edit",
        data={"new_password": "", "role": "admin"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Succesfully updated" in response.data

    with app.app_context():
        updated_user = get_user(user["id"])
        assert updated_user["user_role"] == "admin"


def test_edit_own_password(client, app):
    with app.app_context():
        hashed = generate_password_hash("password")
        post_sql("INSERT INTO users (username, password, user_role) VALUES (:username, :password, :role)",
                     {"username": "user1", "password": hashed, "role": "user"})
        user = get_user_by_username("user1")

    with client.session_transaction() as session:
        session["user_id"] = user["id"]
        session["user_role"] = "user"
        session["username"] = "user1"

    response = client.post(
        f"/users/{user['id']}/edit",
        data={"old_password": "password", "new_password": "password1"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Succesfully updated" in response.data

    with app.app_context():
        updated_user = get_user(user["id"])
        assert check_password_hash(updated_user["password"], "password1")

def test_report(client, app):
    with client.session_transaction() as session:
        session["user_id"] = 1
        session["user_role"] = "user"
        session["username"] = "user1"

    response = client.get('/report')
    assert response.status_code == 200
    assert b"Report" in response.data

def test_report_empty_ip(client, app):
    with client.session_transaction() as session:
        session["user_id"] = 1
        session["user_role"] = "user"
        session["username"] = "user1"

    response = client.post('/report', data={"ip_address": ""}, follow_redirects=True)
    assert response.status_code == 200
    assert b"Enter ip address" in response.data

def test_report_invalid_ip(client, app):
    with client.session_transaction() as session:
        session["user_id"] = 1
        session["user_role"] = "user"
        session["username"] = "user1"

    response = client.post('/report', data={"ip_address": "256.256.256.256"}, follow_redirects=True)
    assert response.status_code == 200
    assert b"Enter valid ip address" in response.data

def test_report_ip(client, app):
    with client.session_transaction() as session:
        session["user_id"] = 1
        session["user_role"] = "user"
        session["username"] = "user1"

    ip = "192.168.1.1"
    ip_hashed = hashlib.sha256(ip.encode()).hexdigest()

    with app.app_context():
        assert get_ip_address(ip_hashed) is None

    response = client.post('/report', data={"ip_address": ip}, follow_redirects=True)
    assert response.status_code == 200
    assert b"You successfully reported ip address" in response.data

    with app.app_context():
        assert get_ip_address(ip_hashed) is not None

def test_report_post_existing_ip(client, app):
    with app.app_context():
        ip = "10.0.0.1"
        ip_hashed = hashlib.sha256(ip.encode()).hexdigest()
        post_sql("INSERT INTO black_list (ip_address) VALUES (:ip_address)", {"ip_address": ip_hashed})

    with client.session_transaction() as session:
        session["user_id"] = 1
        session["user_role"] = "user"
        session["username"] = "user1"

    response = client.post('/report', data={"ip_address": ip}, follow_redirects=True)
    assert response.status_code == 200
    assert b"Ip address already in black list" in response.data