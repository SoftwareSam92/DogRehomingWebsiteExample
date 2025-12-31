# Dog Rehoming Website

A simple website for rehoming dogs, built with Python Flask and Bootstrap.

## Setup

1. Install dependencies: `pip install -r requirements.txt`

2. Run the app: `python app.py`

3. Open http://127.0.0.1:5000/

Note: Photos are placeholders from via.placeholder.com. Replace with actual dog images in the database.

The database (dogs.db) is created automatically with sample data.

## Inspecting the Database

To inspect the SQLite database file `dogs.db`, you can use the sqlite3 command-line tool:

1. Open a terminal in the project directory.

2. Run `sqlite3 dogs.db`

3. Use commands like:

   - `.tables` to list tables

   - `.schema` to see table schemas

   - `SELECT * FROM dogs;` to view dog data

   - `SELECT * FROM users;` to view user data

4. Type `.quit` to exit.