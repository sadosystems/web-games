import os
from pprint import pprint

import eventlet
eventlet.monkey_patch()
from flask import Flask, Request, render_template, request, session, redirect, url_for
from flask_socketio import join_room, leave_room, send, SocketIO

app = Flask(__name__)
app.config["SECRET_KEY"] = "hjhjsdahhds"
socketio = SocketIO(app, async_mode='eventlet') 

rooms = {"plaza": {"members": 0, "messages": []},
         "indoor_a": {"members": 0, "messages": []},
         "indoor_b": {"members": 0, "messages": []},
         "indoor_c": {"members": 0, "messages": []},
         "indoor_d": {"members": 0, "messages": []},
         "indoor_e": {"members": 0, "messages": []},
         "beach": {"members": 0, "messages": []},
         "garden": {"members": 0, "messages": []},}

def handle_room_stuff(room_name):
    room = session.get("room")
    if request.method == "POST":
        room = request.form.get("join_room", False)
        session["room"] = room
        return redirect(url_for(room))

    if room is None or session.get("name") is None or room not in rooms:
        print("Something went wrong", flush=True)
        return redirect(url_for("login"))

    return render_template(f"{room_name}.html", code=room, messages=rooms[room]["messages"])

@app.route("/", methods=["POST", "GET"])
def login():
    session.clear()
    if request.method == "POST":
        name = request.form.get("name")
        session["name"] = name
        room = request.form.get("join_room", False)
        session["room"] = room
        if not name: # replce this with real login flow
            return render_template("login.html", error="Please enter a name.", name=name)
        return redirect(url_for("plaza"))

    return render_template("login.html")

@app.route("/plaza", methods=["POST", "GET"])
def plaza():
    print(rooms, flush=True)
    return handle_room_stuff('plaza')

@app.route("/indoor_a", methods=["POST", "GET"])
def indoor_a():
    return handle_room_stuff('indoor_a')

@app.route("/indoor_b", methods=["POST", "GET"])
def indoor_b():
    return handle_room_stuff('indoor_b')

@app.route("/indoor_c", methods=["POST", "GET"])
def indoor_c():
    return handle_room_stuff('indoor_c')

@app.route("/indoor_d", methods=["POST", "GET"])
def indoor_d():
    return handle_room_stuff('indoor_d')

@app.route("/indoor_e", methods=["POST", "GET"])
def indoor_e():
    return handle_room_stuff('indoor_e')

@app.route("/beach", methods=["POST", "GET"])
def beach():
    return handle_room_stuff('beach')

@app.route("/garden", methods=["POST", "GET"])
def garden():
    return handle_room_stuff('garden')

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
    rooms[room]["messages"].append(content)
    print(f"{session.get('name')} said: {data['data']}")

@socketio.on("connect")
def connect(auth):
    room = session.get("room")
    name = session.get("name")
    if not room or not name:
        return
    if room not in rooms:
        leave_room(room)
        return
    
    join_room(room)
    send({"name": name, "message": "has entered the room"}, to=room)
    rooms[room]["members"] += 1
    print(f"{name} joined room {room}")

@socketio.on("disconnect")
def disconnect():
    room = session.get("room")
    name = session.get("name")
    leave_room(room)

    if room in rooms:
        rooms[room]["members"] -= 1
    
    send({"name": name, "message": "has left the room"}, to=room)
    print(f"{name} has left the room {room}")

if __name__ == "__main__":
    socketio.run(app, port=int(os.environ.get('PORT', 5000)), debug=True)