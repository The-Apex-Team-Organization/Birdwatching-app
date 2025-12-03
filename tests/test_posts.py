import io
from werkzeug.security import generate_password_hash
from Birdwatching.utils.databases import insert_user, get_user_by_username, post_sql, get_post

def create_user_and_post(app):
    with app.app_context():
        password = generate_password_hash("password")
        insert_user("user1", password)
        user = get_user_by_username("user1")

        post_sql(
            "INSERT INTO posts (location, image_path, user_id) VALUES (:location, :image_path, :user_id)",
            {"location": "Old Location", "image_path": "images/some.jpg", "user_id": user["id"]}
        )
        post = get_post(1)
    return user, post

def login_user(client, username="user1", password="password"):
    client.post('/auth/login', data={"username": username, "password": password})
    return client


def test_create_post(client, app):
    with app.app_context():
        from werkzeug.security import generate_password_hash
        password = generate_password_hash('password')
        insert_user('user1', password)

    client.post('/auth/login', data={
        'username': 'user1',
        'password': 'password',
    })
    
    with client.session_transaction() as session:
        assert 'user_id' in session
        assert 'username' in session
        assert 'user_role' in session

    photo = (io.BytesIO(b"Image"), 'test_bird.jpg')
    response = client.post("/posts/create", data={
        "location": "lviv",
        "image": photo
    })
    assert response.status_code == 302

def test_create_post_else(client, app):
    with app.app_context():
        from werkzeug.security import generate_password_hash
        password = generate_password_hash('password')
        insert_user('user1', password)

    client.post('/auth/login', data={
        'username': 'user1',
        'password': 'password',
    })
    
    with client.session_transaction() as session:
        assert 'user_id' in session
        assert 'username' in session
        assert 'user_role' in session

    photo = (io.BytesIO(b"Image"), 'test_bird.jpg')
    response = client.post("/posts/create", data={
        "location": "lviv",
        "image": photo
    })
    assert response.status_code == 302

def test_create_post_invalid_file_type(client, app):
    with app.app_context():
        from werkzeug.security import generate_password_hash
        password = generate_password_hash('password')
        insert_user('user1', password)

    client.post('/auth/login', data={
        'username': 'user1',
        'password': 'password',
    })
    
    with client.session_transaction() as session:
        assert 'user_id' in session
        assert 'username' in session
        assert 'user_role' in session

    photo = (io.BytesIO(b"Image"), 'test_bird.exexexexe')
    response = client.post("/posts/create", data={
        "location": "lviv",
        "image": photo
    })
    assert response.status_code == 302

def test_create_post_both_field_required(client, app):
    with app.app_context():
        from werkzeug.security import generate_password_hash
        password = generate_password_hash('password')
        insert_user('user1', password)

    client.post('/auth/login', data={
        'username': 'user1',
        'password': 'password',
    })
    
    with client.session_transaction() as session:
        assert 'user_id' in session
        assert 'username' in session
        assert 'user_role' in session

    response = client.post("/posts/create", data={
        "location": "lviv",
    })
    assert response.status_code == 302

def test_edit_post_success(client, app):
    user, post = create_user_and_post(app)
    client_logged_in = login_user(client)

    response = client_logged_in.post(
        f"/posts/{post['id']}/edit",
        data={"location": "New Location"},
        follow_redirects=True
    )

    assert response.status_code == 200

    with app.app_context():
        updated_post = get_post(post["id"])
        assert updated_post["location"] == "New Location"

def test_edit_post_missing_location(client, app):
    user, post = create_user_and_post(app)
    client_logged_in = login_user(client)

    response = client_logged_in.post(
        f"/posts/{post['id']}/edit",
        data={"location": ""},
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"location" in response.data

def test_edit_post_invalid_file_type(client, app):
    user, post = create_user_and_post(app)
    client_logged_in = login_user(client)

    data = {
        "location": "New Location",
        "image": (io.BytesIO(b"fake image content"), "file.exe")
    }

    response = client_logged_in.post(
        f"/posts/{post['id']}/edit",
        data=data,
        content_type='multipart/form-data',
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"Invalid" in response.data