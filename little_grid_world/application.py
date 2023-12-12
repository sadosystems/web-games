from flask import Flask, render_template, request
from flask_socketio import SocketIO, join_room
import eventlet
eventlet.monkey_patch()
import boto3
from botocore.exceptions import NoCredentialsError

import json
import random
import os

DEBUG = True

application = Flask(__name__)
application.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(application, async_mode='eventlet') #, async_mode='gevent')

if __name__ == '__main__':
    socketio.run(application, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)