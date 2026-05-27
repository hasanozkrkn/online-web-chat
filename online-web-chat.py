from flask import Flask, render_template, request
from flask_socketio import SocketIO, send, emit, disconnect

app = Flask(__name__)
app.config['SECRET'] = 'secret!123'
socketio = SocketIO(app, cors_allowed_origins='*', async_mode='threading')

# Connected users: {sid: username}
users = {}

# Banned users list
banned_users = []

ADMIN_PASSWORD = "admin123"

@socketio.on('connect')
def handle_connect():
    print(f'New connection: {request.sid}')

@socketio.on('disconnect')
def handle_disconnect():
    if request.sid in users:
        username = users[request.sid]
        del users[request.sid]
        socketio.emit('user_list', list(users.values()))
        socketio.emit('message', f'🔴 {username} has left the chat.')

@socketio.on('join')
def handle_join(data):
    username = data['username']

    # Banned kontrolu
    if username in banned_users:
        emit('banned')
        return

    users[request.sid] = username
    socketio.emit('user_list', list(users.values()))
    socketio.emit('message', f'🟢 {username} has joined the chat.')

@socketio.on('message')
def handle_message(message):
    socketio.emit('message', message)

@socketio.on('kick')
def handle_kick(data):
    password = data.get('password')
    target = data.get('username')

    if password != ADMIN_PASSWORD:
        emit('error', 'Wrong admin password!')
        return

    # Add to banned list
    if target not in banned_users:
        banned_users.append(target)

    # Find and kick the target
    target_sid = None
    for sid, username in users.items():
        if username == target:
            target_sid = sid
            break

    if target_sid:
        socketio.emit('kicked', room=target_sid)
        socketio.emit('message', f'🚫 {target} was kicked by admin.')

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', debug=True, allow_unsafe_werkzeug=True)
