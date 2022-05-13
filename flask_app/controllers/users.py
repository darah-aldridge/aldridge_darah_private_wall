from flask import render_template, request, redirect, session
from flask_app.models.user import User
from flask_app.models.message import Message
from flask_app import app
from flask_bcrypt import Bcrypt
from flask import flash

bcrypt = Bcrypt(app)


@app.route('/')
def index():
    return render_template("index.html")

@app.route('/register', methods=['POST'])
def register():
    if not User.validate_registration(request.form):
        return redirect('/')
    pw_hash = bcrypt.generate_password_hash(request.form['password'])
    data = {
        "first_name": request.form['first_name'],
        "last_name": request.form['last_name'],
        "email": request.form['email'],
        "password": pw_hash
        }
    user_id = User.save(data)
    session['user_id'] = user_id
    session['first_name'] = data['first_name']
    session['last_name'] = data['last_name']
    return redirect('/dashboard')

@app.route('/login', methods=['POST'])
def login():
    data = { 
        "email" : request.form["email"] 
        }
    user = User.get_by_email(data)
    if not user:
        flash(u"Invalid Email/Password", 'login error')
        return redirect("/")
    if not bcrypt.check_password_hash(user.password, request.form['password']):
        flash(u"Invalid Email/Password", 'login error')
        return redirect('/')
    session['user_id'] = user.id
    session['first_name'] = user.first_name
    session['last_name'] = user.last_name
    return redirect('/dashboard')

@app.route('/dashboard')
def show():
    user_id=session['user_id']
    users = User.get_all(user_id)
    receivedMessage = User.get_one_user_with_messages(user_id)
    return render_template("dashboard.html", all_users=users, all_messages=receivedMessage)

@app.route('/log-out')
def clear():
    session.clear()
    return redirect('/')

@app.route('/send_message', methods=['POST'])
def sendMessage():
    if not Message.validate_registration(request.form):
        return redirect('/dashboard')
    data = { 
        "message" : request.form["message"],
        "receiver" : request.form["receiver"],
        "sender_id": session['user_id'],
    }
    message = Message.save(data)
    return redirect('/dashboard')

@app.route('/delete/<int:id>')
def delete(id):
    Message.delete(id)
    return redirect('/dashboard')