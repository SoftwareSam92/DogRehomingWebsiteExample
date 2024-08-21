from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient

app = Flask(__name__)

# MongoDB configuration
client = MongoClient("mongodb://localhost:27017/")
db = client.dog_rehoming
dogs_collection = db.dogs

@app.route('/')
def index():
    dogs = list(dogs_collection.find())
    return render_template('index.html', dogs=dogs)

@app.route('/add_dog', methods=['GET', 'POST'])
def add_dog():
    if request.method == 'POST':
        name = request.form['name']
        breed = request.form['breed']
        age = request.form['age']
        description = request.form['description']
        
        # Insert dog into MongoDB
        dogs_collection.insert_one({
            'name': name,
            'breed': breed,
            'age': age,
            'description': description
        })
        return redirect(url_for('index'))
    return render_template('add_dog.html')

@app.route('/dog/<dog_id>')
def dog_detail(dog_id):
    dog = dogs_collection.find_one({'_id': ObjectId(dog_id)})
    return render_template('dog_detail.html', dog=dog)

if __name__ == '__main__':
    app.run(debug=True)
