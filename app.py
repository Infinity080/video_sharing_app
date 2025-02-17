from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from flask_socketio import SocketIO, emit, disconnect
from werkzeug.utils import secure_filename
import os
import sqlite3

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = {'mp4', 'avi'}
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

current_video = None
current_time = 0
is_playing = False
connected_users = {}
MAX_USERS = 100

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def init_db():
    with sqlite3.connect('database.db') as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL UNIQUE
        )''')

init_db()

@app.route('/')
def index():
    with sqlite3.connect('database.db') as conn:
        videos = conn.execute('SELECT * FROM videos').fetchall()
    return render_template('index.html', videos=videos)


@app.route('/upload', methods=['POST'])
def upload():
    global current_video, current_time, is_playing
    if 'video' not in request.files:
        return redirect(url_for('index'))
    file = request.files['video']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        with sqlite3.connect('database.db') as conn:
            try:
                conn.execute('INSERT INTO videos (filename) VALUES (?)', (filename,))
                conn.commit()
            except sqlite3.IntegrityError:
                pass
        current_video = filename
        current_time = 0
        is_playing = False
        socketio.emit('new_video', {'filename': filename, 'timestamp': current_time, 'is_playing': is_playing})
        return redirect(url_for('index'))
    return redirect(url_for('index'))


@app.route('/play', methods=['POST'])
def play_video():
    global current_video, current_time, is_playing
    filename = request.form.get('filename')
    if filename:
        current_video = filename
        current_time = 0
        is_playing = False
        socketio.emit('new_video', {'filename': current_video, 'timestamp': current_time, 'is_playing': is_playing})

        
    return redirect(url_for('index'))


@app.route('/uploads/<filename>')
def serve_video(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@socketio.on('connect')
def on_connect():
    if len(connected_users) >= MAX_USERS:
        emit('error', {'message': 'Server is full. Please try again later.'})
        disconnect()
        return
    user_id = request.sid
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    connected_users[user_id] = {'sid': user_id, 'ip': user_ip}
    global current_video, current_time, is_playing
    if current_video:
        emit('new_video', {'filename': current_video, 'timestamp': current_time, 'is_playing': is_playing})
    emit('update_users', {'users': list(connected_users.values())}, broadcast=True)


@socketio.on('disconnect')
def on_disconnect():
    user_id = request.sid
    if user_id in connected_users:
        del connected_users[user_id]
    emit('update_users', {'users': list(connected_users.values())}, broadcast=True)


@socketio.on('sync_time')
def sync_time(data):
    global current_time
    current_time = data['timestamp']
    emit('sync_time', {'timestamp': current_time}, broadcast=True, include_self=False)

@socketio.on('play_pause')
def play_pause(data):
    global is_playing
    is_playing = data['is_playing']
    emit('play_pause', {'is_playing': is_playing}, broadcast=True, include_self=False)
    if is_playing:
        emit('sync_time', {'timestamp': current_time}, broadcast=True, include_self=False)


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
