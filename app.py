from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO, join_room

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/chat')
def chat():
    username = request.args.get('username')
    room = request.args.get('room')

    if username and room:
        return render_template("chat_T.html")
    else:
        return redirect(url_for('home'))

@socketio.on('send_message')
def hendle_send_message_event(data):
    app.logger.info("{} has sent message to the room {}: {}".format(data['username'], data['room'], data['message']))
    socketio.emit('recieve_message', data, room=data['room'])


@socketio.on('join_room')
def handle_join_room_event(data):
    app.logger.info("{} has joined the room {}".format(data['username'], data['room']))
    join_room(data['room'])
    socketio.emit('join_room_anouncement', data)

if __name__ == '__main__':
    socketio.run(app, debug=True)