from flask import Flask, render_template, request, redirect, session, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId
from dotenv import load_dotenv
import os
from werkzeug.security import generate_password_hash, check_password_hash
from flask import render_template, request, redirect, url_for, session

from pymongo import MongoClient

# Replace with your actual MongoDB connection string and database name
client = MongoClient("mongodb+srv://elzasabub23cs1226:elza@note.cft27z0.mongodb.net/test?retryWrites=true&w=majority")
db = client['personalnotes']
notes_collection = db['notes']


load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

# Connect to MongoDB
client = MongoClient(os.getenv("MONGO_URI"))
db = client["personalnotes"]
users = db["users"] 
notes = db["notes"]

# Home Route
@app.route("/")
def home():
    return redirect("/login")

# Register
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = generate_password_hash(request.form["password"])
        if users.find_one({"username": username}):
            return redirect("/exists")
        users.insert_one({"username": username, "password": password})
        return redirect("/login")
    return render_template("register.html")

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users.find_one({'username': username})
        if user and check_password_hash(user['password'], password):
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            # handle invalid login
            pass
    return render_template('login.html')

# Dashboard - Show Notes
@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    print("Logged in as:", session['username'])  # <--- Add this line
    notes = list(notes_collection.find({'user': session['username'].strip().lower()}))
    print("Notes found:", notes)  # <--- Add this line
    return render_template('dashboard.html', notes=notes, username=session['username'])
# Create New Note
"""
@app.route("/note/new", methods=["GET", "POST"])
def new_note():
    if "user_id" not in session:
        return redirect("/login")
    if request.method == "POST":
        notes.insert_one({
            "user_id": session["user_id"],
            "title": request.form["title"],
            "content": request.form["content"]
        })
        return redirect("/dashboard")
    return render_template("new_note.html") """

@app.route('/edit_note/<note_id>', methods=['GET', 'POST'])
def edit_note(note_id):
    note = notes_collection.find_one({'_id': ObjectId(note_id)})
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        notes_collection.update_one(
            {'_id': ObjectId(note_id)},
            {'$set': {'title': title, 'content': content}}
        )
        return redirect(url_for('dashboard'))
    return render_template('edit_note.html', note=note)

@app.route('/delete_note/<note_id>')
def delete_note(note_id):
    notes_collection.delete_one({'_id': ObjectId(note_id)})
    return redirect(url_for('dashboard'))

@app.route('/new_note', methods=['GET', 'POST'])
def new_note():
    if request.method == 'POST':
        # Get note data from form
        title = request.form['title']
        content = request.form['content']
        notes_collection.insert_one({
    'title': title,
    'content': content,
    'user': session['username'].strip().lower()   # or 'username': session['username']
})
        # Save the note to the database (implement this part as per your DB setup)
        # Example: notes_collection.insert_one({'title': title, 'content': content, 'user': session['username']})
        return redirect(url_for('dashboard'))
    return render_template('new_note.html')

"""
# Delete Note
@app.route("/note/delete/<note_id>")
def delete_note(note_id):
    if "user_id" not in session:
        return redirect("/login")
    notes.delete_one({"_id": ObjectId(note_id), "user_id": session["user_id"]})
    return redirect("/dashboard")

"""


# Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

if __name__ == "__main__":
    app.run(debug=True)
