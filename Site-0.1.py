from flask import Flask, render_template, request, jsonify
import json
import socket
from datetime import datetime
import threading

app = Flask(__name__)
app.static_url_path = '/assets'
app.static_folder = 'assets'

def save_message_to_json(username, message):
    timestamp = str(datetime.now())
    data = {"username": username, "message": message}
    with open("assets/storage/data.json", "r") as json_file:
        messages = json.load(json_file)
    messages[timestamp] = data
    with open("assets/storage/data.json", "w") as json_file:
        json.dump(messages, json_file, indent=2)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/message", methods=["GET", "POST"])
def message():
    if request.method == "POST":
        username = request.form["username"]
        message = request.form["message"]
        save_message_to_json(username, message)
    return render_template("message.html")

@app.route("/assets/<path:filename>")
def static_files(filename):
    return app.send_static_file(filename)

@app.errorhandler(404)
def page_not_found(e):
    return render_template("error.html"), 404

def socket_server():
    UDP_IP = "127.0.0.1"
    UDP_PORT = 5000

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))

    while True:
        data, addr = sock.recvfrom(1024)
        try:
            data_dict = json.loads(data)
            username = data_dict.get("username", "")
            message = data_dict.get("message", "")
            save_message_to_json(username, message)
        except json.JSONDecodeError:
            pass

if __name__ == "__main__":
    socket_thread = threading.Thread(target=socket_server)
    socket_thread.daemon = True
    socket_thread.start()

    app.run(port=3000)