from flask import session, redirect, url_for, render_template, request
from dataclasses import dataclass, field

@dataclass
class Room():
    name: str
    members: int = 0
    messages: list = field(default_factory=list)

rooms = {
    "plaza": Room(name="plaza"),
    "indoor_a": Room(name="indoor_a"),
    "indoor_b": Room(name="indoor_b"),
    "indoor_c": Room(name="indoor_c"),
    "indoor_d": Room(name="indoor_d"),
    "indoor_e": Room(name="indoor_e"),
    "beach": Room(name="beach"),
    "garden": Room(name="garden"),
}

def handle_room_stuff(room_name: str, rooms: dict[str, Room]):
    if room_name not in rooms:
        return redirect(url_for("login"))
    if request.method == "POST":
        room = request.form.get("join_room", False)
        session["room"] = room
        return redirect(url_for('room', room_name=room))
    
    room = session.get("room")
    if room is None or session.get("name") is None or room not in rooms:
        print("Something went wrong", flush=True)
        return redirect(url_for("login"))

    return render_template(f"{room_name}.html", code=room, messages=rooms[room].messages)