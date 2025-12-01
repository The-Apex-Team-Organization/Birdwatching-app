import pytest
from Birdwatching import create_app
from Birdwatching.utils.databases import Base, init_db, insert_user 
from werkzeug.security import generate_password_hash

@pytest.fixture()
def app():
    app = create_app()

    app.config["SECRET_KEY"] = "testkey123"
    app.config["DATABASE_URL"] = "sqlite:///:memory:"

    init_db(app)
    from Birdwatching.utils.databases import engine

    with app.app_context():
        Base.metadata.create_all(engine)
        
        password_hash = generate_password_hash('password')
        insert_user('user', password_hash) 

    yield app

    with app.app_context():
        Base.metadata.drop_all(engine)

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def login_user(client):
    def _login_user(username="user", password="password"):
        return client.post('/auth/login', data={"username": username, "password": password})
    return _login_user