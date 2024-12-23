from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import random

app = Flask(__name__)
socketio = SocketIO(app)

#Store connected users
users = {}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on("connect")
def handle_connect():
    username = f"User_{random.randint(1000,9999)}"
    gender = random.choice(["girl","boy"])
    avatar_url = f"https://api.dicebear.com/6.x/adventurer/svg?seed={username}&gender={gender}"

    users[request.sid] = {"username":username,"avatar":avatar_url}

    emit("user_joined", {"username":username,"avatar":avatar_url}, broadcast=True)

    emit("set_username", {"username":username, "avatar": avatar_url})

@socketio.on("disconnect")
def handle_disconnect():
    user = users.pop(request.sid, None)
    if user:
        emit("user_left", {"username":user["username"]}, broadcast=True)

@socketio.on("send_message")
def handle_message(data):
    user = users.get(request.sid)
    if user:
        emit("new_message", {"username":user["username"], "avatar":user["avatar"],"message":data["message"]}, 
             broadcast=True)
        
@socketio.on("update_username")
def handle_update_username(data):
    old_username = users[request.sid]["username"]
    new_username = data["new_username"]
    users[request.sid]["username"] = new_username

    emit("username_updated", {"old_username":old_username,"new_username":new_username}, broadcast =True)
         
if __name__ == "__main__":
    socketio.run(app)