"""
Dog Rehoming Website

A Flask-based web application for rehoming dogs. Users can register, log in,
browse available dogs, add them to a basket, and complete checkout.

Features:
- User authentication with Flask-Login
- SQLite database for storing users and dogs
- Basket functionality for adopting multiple dogs
- Responsive UI with Bootstrap

Author: [Your Name]
Date: [Current Date]
"""

from flask import Flask, render_template, g, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this to a random secret key

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    """
    User model for Flask-Login.

    Represents a registered user with id, username, and email.
    """
    def __init__(self, id, username, email):
        self.id = id
        self.username = username
        self.email = email

@login_manager.user_loader
def load_user(user_id):
    """
    Load a user by ID for Flask-Login.

    Args:
        user_id (str): The user's ID.

    Returns:
        User: The User object if found, else None.
    """
    db = get_db()
    cur = db.execute('SELECT id, username, email FROM users WHERE id = ?', (user_id,))
    user = cur.fetchone()
    if user:
        return User(user[0], user[1], user[2])
    return None

def get_db():
    """
    Get the database connection for the current request.

    Uses Flask's g object to store the connection.

    Returns:
        sqlite3.Connection: The database connection.
    """
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config.get('DATABASE', 'dogs.db'))
    return db

@app.teardown_appcontext
def close_connection(exception):
    """
    Close the database connection at the end of the request.

    Args:
        exception: Any exception that occurred during the request.
    """
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    """
    Initialize the database with tables and sample data.

    Creates users and dogs tables if they don't exist,
    and populates dogs with sample entries.
    """
    with app.app_context():
        db = get_db()
        # Create users table
        db.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )''')
        # Create dogs table
        db.execute('''CREATE TABLE IF NOT EXISTS dogs (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            price REAL NOT NULL,
            photo_url TEXT NOT NULL
        )''')
        db.commit()
        # Populate with sample data
        db.execute("INSERT OR IGNORE INTO dogs (id, name, description, price, photo_url) VALUES (1, 'Buddy', 'Friendly golden retriever, loves kids.', 150.0, 'https://images.unsplash.com/photo-1552053831-71594a27632d?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=300&q=80')")
        db.execute("INSERT OR IGNORE INTO dogs (id, name, description, price, photo_url) VALUES (2, 'Max', 'Energetic border collie, great for active families.', 200.0, 'https://images.unsplash.com/photo-1583337130417-3346a1be7dee?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=300&q=80')")
        db.execute("INSERT OR IGNORE INTO dogs (id, name, description, price, photo_url) VALUES (3, 'Bella', 'Sweet beagle, perfect companion.', 120.0, 'https://images.unsplash.com/photo-1587300003388-59208cc962cb?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=300&q=80')")
        db.commit()

@app.route('/')
def index():
    """
    Home page displaying all available dogs.

    Returns:
        Rendered template with list of dogs.
    """
    db = get_db()
    cur = db.execute('SELECT id, name, description, price, photo_url FROM dogs')
    dogs = cur.fetchall()
    return render_template('index.html', dogs=dogs)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Handle user registration.

    GET: Show registration form.
    POST: Process registration form, create user if valid.
    """
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        password_hash = generate_password_hash(password)
        db = get_db()
        try:
            db.execute('INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)', (username, email, password_hash))
            db.commit()
            flash('Registration successful! Please log in.')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username or email already exists.')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handle user login.

    GET: Show login form.
    POST: Authenticate user and log in if valid.
    """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        cur = db.execute('SELECT id, username, email, password_hash FROM users WHERE username = ?', (username,))
        user_data = cur.fetchone()
        if user_data and check_password_hash(user_data[3], password):
            user = User(user_data[0], user_data[1], user_data[2])
            login_user(user)
            return redirect(url_for('index'))
        flash('Invalid username or password.')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """
    Log out the current user.

    Requires login.
    """
    logout_user()
    return redirect(url_for('index'))

@app.route('/add_to_basket/<int:dog_id>')
@login_required
def add_to_basket(dog_id):
    """
    Add a dog to the user's basket.

    Args:
        dog_id (int): The ID of the dog to add.

    Requires login.
    """
    if 'basket' not in session:
        session['basket'] = []
    if dog_id not in session['basket']:
        session['basket'].append(dog_id)
        session.modified = True
    flash('Dog added to basket!')
    return redirect(url_for('index'))

@app.route('/basket')
@login_required
def basket():
    """
    Display the user's basket with selected dogs and total price.

    Requires login.
    """
    basket_ids = session.get('basket', [])
    if basket_ids:
        db = get_db()
        placeholders = ','.join('?' for _ in basket_ids)
        cur = db.execute(f'SELECT id, name, description, price, photo_url FROM dogs WHERE id IN ({placeholders})', basket_ids)
        dogs = cur.fetchall()
    else:
        dogs = []
    total = sum(dog[3] for dog in dogs)
    return render_template('basket.html', dogs=dogs, total=total)

@app.route('/remove_from_basket/<int:dog_id>')
@login_required
def remove_from_basket(dog_id):
    """
    Remove a dog from the user's basket.

    Args:
        dog_id (int): The ID of the dog to remove.

    Requires login.
    """
    if 'basket' in session and dog_id in session['basket']:
        session['basket'].remove(dog_id)
        session.modified = True
    return redirect(url_for('basket'))

@app.route('/checkout')
@login_required
def checkout():
    """
    Process checkout for the user's basket.

    Clears the basket and shows confirmation.
    In a real app, payment processing would be added here.

    Requires login.
    """
    basket_ids = session.get('basket', [])
    if not basket_ids:
        flash('Your basket is empty.')
        return redirect(url_for('basket'))
    db = get_db()
    placeholders = ','.join('?' for _ in basket_ids)
    cur = db.execute(f'SELECT id, name, description, price, photo_url FROM dogs WHERE id IN ({placeholders})', basket_ids)
    dogs = cur.fetchall()
    total = sum(dog[3] for dog in dogs)
    # In a real app, process payment here
    session['basket'] = []  # Clear basket
    session.modified = True
    flash('Checkout successful! Thank you for adopting.')
    return render_template('checkout.html', dogs=dogs, total=total)

@app.route('/dog/<int:dog_id>')
def dog(dog_id):
    """
    Display details for a specific dog.

    Args:
        dog_id (int): The ID of the dog.

    Returns:
        Rendered template with dog details or 404 if not found.
    """
    db = get_db()
    cur = db.execute('SELECT id, name, description, price, photo_url FROM dogs WHERE id = ?', (dog_id,))
    dog = cur.fetchone()
    if dog:
        return render_template('dog.html', dog=dog)
    else:
        return 'Dog not found', 404

if __name__ == '__main__':
    # Initialize the database on startup
    init_db()
    # Run the Flask app in debug mode
    app.run(debug=True)