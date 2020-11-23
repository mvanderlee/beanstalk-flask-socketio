import random
from threading import Lock

from flask import Flask, render_template
from flask_socketio import SocketIO, emit

from .loading_messages import loading_messages

# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = 'eventlet'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()


def background_thread():
    """Example of how to send server generated events to clients."""
    while True:
        socketio.sleep(10)
        print('emitting background generated message')
        socketio.emit('stream_response', random.choice(loading_messages), namespace='/socketio')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/loading_message', methods=['GET'])
def loading_message():
    print('loading_message')
    return random.choice(loading_messages)


@socketio.on('my_message', namespace='/socketio')
def handle_message(message):
    print('handle_message')
    emit('my_response', f'Your message "{message}" is stupid!')


@socketio.on('stream', namespace='/socketio')
def handle_stream():
    print('handle_stream')
    emit('stream_response', random.choice(loading_messages), broadcast=True)


@socketio.on('connect', namespace='/socketio')
def test_connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(background_thread)
    emit('my_response', {'data': 'Connected', 'count': 0})


if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", debug=False)

    print('Started beanstalk app')
