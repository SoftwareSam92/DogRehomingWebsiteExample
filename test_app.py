import pytest
import sqlite3
import os
import uuid
from app import app, get_db, init_db, User
from flask import g

@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    db_path = f'test_{uuid.uuid4().hex}.db'
    app.config['TESTING'] = True
    app.config['DATABASE'] = db_path  # Use unique file database for tests
    with app.app_context():
        init_db()  # Initialize the test database
        with app.test_client() as client:
            yield client
    # Clean up
    if os.path.exists(db_path):
        os.remove(db_path)

@pytest.fixture
def db():
    """Provide a test database connection."""
    conn = sqlite3.connect(':memory:')
    init_db()  # This will create tables in the in-memory db
    yield conn
    conn.close()

def test_index(client):
    """Test the index page loads correctly."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Dog Rehoming' in response.data  # Assuming the title is in the template

def test_register(client):
    """Test user registration."""
    response = client.post('/register', data={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password123'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Registration successful' in response.data

def test_register_duplicate_username(client):
    """Test registration with duplicate username fails."""
    # First registration
    client.post('/register', data={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password123'
    })
    # Second registration with same username
    response = client.post('/register', data={
        'username': 'testuser',
        'email': 'test2@example.com',
        'password': 'password123'
    }, follow_redirects=True)
    assert b'Username or email already exists' in response.data

def test_login(client):
    """Test user login."""
    # Register first
    client.post('/register', data={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password123'
    })
    # Then login
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'password123'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Logout' in response.data  # Check for logout link indicating logged in

def test_login_invalid(client):
    """Test login with invalid credentials."""
    response = client.post('/login', data={
        'username': 'wronguser',
        'password': 'wrongpass'
    }, follow_redirects=True)
    assert b'Invalid username or password' in response.data

def test_add_to_basket_requires_login(client):
    """Test that adding to basket requires login."""
    response = client.get('/add_to_basket/1', follow_redirects=True)
    assert response.status_code == 200
    assert b'Please log in' in response.data or b'login' in response.data.lower()  # Assuming redirect to login

def test_dog_detail(client):
    """Test viewing a specific dog's details."""
    response = client.get('/dog/1')
    assert response.status_code == 200
    assert b'Buddy' in response.data  # Assuming the dog name is displayed

def test_dog_not_found(client):
    """Test viewing a non-existent dog."""
    response = client.get('/dog/999')
    assert response.status_code == 404
    assert b'Dog not found' in response.data

def test_get_db():
    """Test database connection."""
    with app.app_context():
        db = get_db()
        assert isinstance(db, sqlite3.Connection)

def test_user_model():
    """Test the User model."""
    user = User(1, 'testuser', 'test@example.com')
    assert user.id == 1
    assert user.username == 'testuser'
    assert user.email == 'test@example.com'