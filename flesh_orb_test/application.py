import os
from dataclasses import dataclass, field
from enum import Enum

import eventlet
eventlet.monkey_patch()
from flask import Flask, Request, render_template, request, session, redirect, url_for
from flask_socketio import join_room, leave_room, send, SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
from sqlalchemy import Enum

from room_helpers import handle_room_stuff, rooms
from user_helpers import Elevation

app = Flask(__name__)
app.config["SECRET_KEY"] = "hjhjsdahhds"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

socketio = SocketIO(app, async_mode='eventlet') 
bcrypt = Bcrypt(app)
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    elevation = db.Column(db.Enum(Elevation), default=Elevation.GUEST)
    money = db.Column(db.Float, default=0)
class RegisterForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=3, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=3, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Login')

@app.route('/')
def home():
    return render_template('home.html')

@app.route("/login", methods=["POST", "GET"])
def login():
    error = ''
    form = LoginForm()
    default_username = session.get("name")
    if request.method == 'GET':
        form.username.data = default_username
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                session["room"] = 'plaza'
                session["name"] = user.username
                login_user(user)
                return redirect(url_for('room', room_name='plaza'))
            else:
                error = "Invalid password"
        else:
            print("GOT HERE", flush=True)
            error = "Invalid username"
            
    return render_template('login.html', form=form, error=error)

@app.route("/register", methods=["POST", "GET"])
def register():
    form = RegisterForm()
    error = None
    if form.validate_on_submit():
        name = form.username.data
        existing_user_username = User.query.filter_by(username=name).first()
        if existing_user_username:
            error = 'Username already taken.'
        else:
            session['name'] = name
            hashed_password = bcrypt.generate_password_hash(form.password.data)
            new_user = User(username=name, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))
        
    return render_template("register.html", form=form, error=error)

@app.route("/<room_name>", methods=["GET", "POST"])
def room(room_name):
    return handle_room_stuff(room_name, rooms)

@socketio.on("message")
def message(data):
    room = session.get("room")
    if room not in rooms:
        return 
    
    content = {
        "name": session.get("name"),
        "message": data["data"]
    }
    send(content, to=room)
    rooms[room].messages.append(content)
    print(f"{session.get('name')} said: {data['data']}")

@socketio.on("connect")
def connect(auth):
    print(f"here it is: {auth}", flush=True)
    room = session.get("room")
    name = session.get("name")
    if not room or not name:
        return
    if room not in rooms:
        leave_room(room)
        return
    
    join_room(room)
    send({"name": name, "message": "has entered the room"}, to=room)
    rooms[room].members += 1
    print(f"{name} joined room {room}")

@socketio.on("disconnect")
def disconnect():
    room = session.get("room")
    name = session.get("name")
    leave_room(room)

    if room in rooms:
        rooms[room].members -= 1
    
    send({"name": name, "message": "has left the room"}, to=room)
    print(f"{name} has left the room {room}")

if __name__ == "__main__":
    socketio.run(app, port=int(os.environ.get('PORT', 5000)), debug=True)