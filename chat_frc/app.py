from datetime import datetime

from bson.json_util import dumps
from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_socketio import SocketIO, join_room, leave_room
from pymongo.errors import DuplicateKeyError

from .db import DbUser, DbRoom

app = Flask(__name__)
app.secret_key = "sfdjkafnk"
socketio = SocketIO(app)
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

db_user = DbUser('mongodb+srv://mizaellocal:AB123456@cluster0.fzucq6j.mongodb.net/?retryWrites=true&w=majority','ChatDB','users')
db_room = DbRoom('mongodb+srv://mizaellocal:AB123456@cluster0.fzucq6j.mongodb.net/?retryWrites=true&w=majority','ChatDB','rooms','members')

@app.route('/')
def home():
    rooms = []
    if current_user.is_authenticated():
        rooms = db_room.get_rooms_for_user(current_user.username)
    return render_template("index.html", rooms=rooms)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    message = ''
    if request.method == 'POST':
        username = request.form.get('usuario')
        password_input = request.form.get('senha')
        user = db_user.get_user(username)

        if user and user.check_password(password_input):
            login_user(user)
            return redirect(url_for('home'))
        else:
            message = 'Senha ou usuario incorretos!'
    return render_template('login.html', message=message)


@app.route('/cadastro', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    message = ''
    if request.method == 'POST':
        username = request.form.get('usuario')
        password = request.form.get('senha')
        print(username)
        print(password)
        try:
            db_user.insert_user(username, password)
            return redirect(url_for('login'))
        except DuplicateKeyError:
            message = "Usuario ja cadastrado!"
    return render_template('cadastro.html', message=message)


@app.route("/logout/")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))



@app.route('/cria-sala/', methods=['GET', 'POST'])
@login_required
def create_room():
    message = ''
    if request.method == 'POST':
        room_number = request.form.get('numero_sala')
        usernames = [username.strip() for username in request.form.get('membros').split(',')]

        if len(room_number) and len(usernames):
            room_id = db_room.add_room_chat(int(room_number), current_user.username)
            if current_user.username in usernames:
                usernames.remove(current_user.username)
            db_room.add_room_users(room_id, int(room_number), usernames)
            return redirect(url_for('chat', room_id=room_id))
        else:
            message = "Nao foi possivel criar a sala"
    return render_template('cria_salas.html', message=message)


@app.route('/rooms/<room_id>/')
@login_required
def chat(room_id):
    room = db_room.get_room(room_id)
    if room and db_room.is_room_member(room_id, current_user.username):
        room_members = db_room.get_room_members(room_id)
        return render_template('chat.html', username=current_user.username, room=room, room_members=room_members)
    else:
        return "Room not found", 404

@socketio.on('send_message')
def handle_send_message_event(data):
    app.logger.info("{} has sent message to the room {}: {}".format(data['username'],
                                                                    data['room'],
                                                                    data['message']))
    socketio.emit('receive_message', data, room=data['room'])


@socketio.on('join_room')
def handle_join_room_event(data):
    app.logger.info("{} has joined the room {}".format(data['username'], data['room']))
    join_room(data['room'])
    socketio.emit('join_room_announcement', data, room=data['room'])

@socketio.on('leave_room')
def handle_leave_room_event(data):
    app.logger.info("{} has left the room {}".format(data['username'], data['room']))
    leave_room(data['room'])
    socketio.emit('leave_room_announcement', data, room=data['room'])


@login_manager.user_loader
def load_user(username):
    return db_user.get_user(username)

if __name__ == '__main__':
        socketio.run(app, debug=True)
