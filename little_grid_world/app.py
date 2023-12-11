from flask import Flask, render_template, request
from flask_socketio import SocketIO, join_room
import eventlet
eventlet.monkey_patch()
import boto3

import json
import random
import os

GRID_X = 104
GRID_Y = 104

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app, async_mode='eventlet') #, async_mode='gevent')

# Helper functions
def save_as_json(data, filename):
    try:
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        print(f"Data has been successfully saved to {filename}")
    except Exception as e:
        print(f"An error occurred while saving the data to {filename}: {e}")

def load_json(file):
    try:
        with open(f'{file}.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}
    
def random_color():
    r = random.randint(0, 240)
    g = random.randint(0, 200)
    b = random.randint(0, 240)
    color = "#{:02x}{:02x}{:02x}".format(r, g, b)
    luma = (0.299 * r + 0.587 * g + 0.114 * b) *0.7
    if luma > 128:
        fg_color = '#000000'  # black
    else:
        fg_color = '#ffffff'  # white
    return color, fg_color

def birth_player(player_id):
    skin_color, face_color = random_color()
    players[player_id] = {'x': 2, 'y': 2, 'color': skin_color, 'face_color':face_color}

def color_at_cordinate(x, y):
    return colored_squares[x + y * GRID_Y]

def name_at_cordinate(x, y):
    return squares_names[x + y * GRID_Y]

# Main player behaviour
colored_squares = load_json('data/data')
squares_names = load_json('data/blame')

players = {}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.event
def player_move(data):
    player_id = data['player_id']
    move = data['direction']
    previous_x = players[player_id]['x']
    previous_y = players[player_id]['y']
    previous_color = color_at_cordinate(previous_x, previous_y)
    # Update player positions based on the move
    if move == 'w' and players[player_id]['y'] > 2:
        players[player_id]['y'] -= 1
    elif move == 's' and players[player_id]['y'] <= GRID_Y-4:
        players[player_id]['y'] += 1
    elif move == 'a' and players[player_id]['x'] > 2:
        players[player_id]['x'] -= 1
    elif move == 'd' and players[player_id]['x'] <= GRID_X-4:
        players[player_id]['x'] += 1
    socketio.emit('draw_players', {'players':players, 
                                   'x':previous_x, 
                                   'y':previous_y, 
                                   'previous_color':previous_color})
    return True

@socketio.on('color_square')
def color_square(data):
    player_id = data['player_id']
    y = players[player_id]['y']
    x = players[player_id]['x']
    color = players[player_id]['color']
    try:
        blame = players[player_id]['username']
    except:
        blame = ""
    index = x + y * GRID_Y
    squares_names[index] = blame
    colored_squares[index] = color
    with open('data/data.json', 'w') as file:
        json.dump(colored_squares, file)
    with open('data/blame.json', 'w') as file:
        json.dump(squares_names, file)

    socketio.emit('update_local_squares', {'color': color, 'x':x, 'y':y})

# Handle connections
@socketio.on('connect')
def handle_connect():
    socketio.emit('ask_for_player_id')

@socketio.on('after_connect')
def after_connect(data):
    # player_id = data['player_id']
    session_id = request.sid
    if data not in players:
        birth_player(data)
    socketio.emit('paint_grid', {'players':players, 'squares':colored_squares})

@socketio.on('fetch_blame')
def fetch_blame(data):
    name = name_at_cordinate(data['x'],data['y'])
    socketio.emit('return_blame', name)

@socketio.on('color_change')
def color_change(data):
    player_id = data['player_id']
    color:str = data['color']
    players[player_id]['color'] = color
    hex_color = color.lstrip('#')
    r,g,b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    luma = (0.299 * r + 0.587 * g + 0.114 * b) *0.7
    if luma > 128:
        fg_color = '#000000'  # black
    else:
        fg_color = '#ffffff'  # white
    players[player_id]['face_color'] = fg_color
    socketio.emit('update_positions', {'players':players}, to=player_id)

@socketio.on('name_change')
def name_change(data):
    player_id = data['player_id']
    username:str = data['username']
    players[player_id]['username'] = username

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)