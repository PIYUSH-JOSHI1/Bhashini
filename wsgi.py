
from app import app
from flask_socketio import SocketIO, emit

socketio = SocketIO(app)

if __name__ == '__main__':
    socketio.run(app, debug=True)