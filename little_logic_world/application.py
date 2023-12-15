import json
from random import randint
import os
from typing import Literal
import threading 
import time

from flask import Flask, render_template, request
from flask_socketio import SocketIO
import eventlet
eventlet.monkey_patch()
import boto3
from botocore.exceptions import NoCredentialsError

import circuit_sim

DEBUG = True
GRID_X = 20
GRID_Y = 20

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app, async_mode='eventlet') 

# buckets
s3_client = boto3.client('s3')
bucket_name = 'grid-world-bucket'

# Helper functions
def save_json(data, filename):
    if DEBUG:
        try:
            with open(filename, 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
            print(f"Data has been successfully saved to {filename}")
        except Exception as e:
            print(f"An error occurred while saving the data to {filename}: {e}")
    else:
        try:
            s3_client.put_object(Body=json.dumps(data, ensure_ascii=False, indent=4), 
                                 Bucket=bucket_name, 
                                 Key=filename)
            print(f"Data has been successfully saved to {filename} in S3 bucket")
        except NoCredentialsError:
            print("Credentials not available for AWS S3")

def load_json(filename):
    if DEBUG:
        try:
            with open(f'{filename}.json', 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            return {}
    else:
        try:
            response = s3_client.get_object(Bucket=bucket_name, Key=filename)
            data = response['Body'].read()
            return json.loads(data)
        except Exception as e:
            print(f"An error occurred while loading the data from {filename}: {e}")
            return {}
    
def random_color() -> tuple[str, Literal['#000000', '#ffffff']]:
    r, g, b = [randint(0, 240) for _ in range(3)]
    color = "#{:02x}{:02x}{:02x}".format(r, g, b)
    luma = (0.299 * r + 0.587 * g + 0.114 * b) *0.7
    if luma > 128:
        fg_color = '#000000'  # black
    else:
        fg_color = '#ffffff'  # white
    return color, fg_color

def birth_player(player_id):
    skin_color = 0x1
    face_color = '#ffffff'
    players[player_id] = {'x': randint(2, GRID_X), 
                          'y': randint(2, GRID_Y), 
                          'color': skin_color, 
                          'face_color':face_color}

def cords_to_index(x, y):
    return x + y * GRID_Y

def data_at_cordinate(x, y, table):
    i = cords_to_index(x, y)
    return table[i]

# initialize stuff
grid_lock = threading.Lock()
with grid_lock:
    colored_squares = load_json('data/data')
squares_names = load_json('data/blame')
players = {}

# circuit sim
grid_lock = threading.Lock()

def simulate_electricity():
    global colored_squares
    while True:
        with grid_lock:
            colored_squares = load_json('data/data')
            colored_squares = circuit_sim.simulate(colored_squares)
            # print( colored_squares, flush = True)
            socketio.emit('paint_grid', {'players':players, 
                                         'squares':colored_squares})
        time.sleep(0.1)

# Background task

# handlers 

@app.route('/')
def index():
    return render_template('index.html')

@socketio.event
def player_move(data):
    player_id = data['player_id']
    player = players[player_id]

    move = data['direction']
    x = player['x']
    y = player['y']
    previous_color = data_at_cordinate(x, y, colored_squares)

    if move == 'w' and y > 0:
        players[player_id]['y'] -= 1
    elif move == 's' and y <= GRID_Y-2:
        players[player_id]['y'] += 1
    elif move == 'a' and x > 0:
        players[player_id]['x'] -= 1
    elif move == 'd' and x <= GRID_X-2:
        players[player_id]['x'] += 1

    socketio.emit('draw_players', {'players':players, 
                                   'x':x, 
                                   'y':y, 
                                   'previous_color':previous_color})
    return True

@socketio.on('color_square')
def color_square(data):
    player_id = data['player_id']
    player = players[player_id]
    y = player['y']
    x = player['x']
    color = player['color']

    try:
        blame = player['username']
    except:
        blame = ""

    index = cords_to_index(x, y)

    with grid_lock:  # Acquire the lock before modifying the shared resources
        colored_squares[index] = color
        squares_names[index] = blame
        save_json(colored_squares, 'data/data.json')
        save_json(squares_names, 'data/blame.json')

        socketio.emit('update_local_squares', {'color': color, 
                                            'x':x, 
                                            'y':y})
        
@socketio.on('color_square_click')
def color_square_click(data):
    y = data['y']
    x = data['x']
    color = data['color']

    index = cords_to_index(x, y)

    with grid_lock:
        colored_squares[index] = color
        save_json(colored_squares, 'data/data.json')
        socketio.emit('update_local_squares', {'color': color, 
                                            'x':x, 
                                            'y':y})
@socketio.on('connect')
def handle_connect():
    socketio.emit('ask_for_player_id')

@socketio.on('after_connect')
def after_connect(data):
    session_id = request.sid
    if data not in players:
        birth_player(data)
    with grid_lock:
        socketio.emit('paint_grid', {'players':players, 
                                    'squares':colored_squares})

@socketio.on('fetch_blame')
def fetch_blame(data):
    name = data_at_cordinate(data['x'],
                             data['y'], 
                             squares_names)
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
    threading.Thread(target=simulate_electricity, daemon=True).start()
    socketio.run(app, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)
