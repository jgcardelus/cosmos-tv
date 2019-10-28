from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

import io
import os
import socket

import config
import compiler

# SERVER VARS
port = config.port

# CREATE SERVER
web = Flask("cosmostv")
web.config["SECRET_KEY"] = "cosmostv"

# CREATE WEBSOCKET
server = SocketIO(web)

# CONNECTION VALIDATION
@server.on("validate_connection")
def validate_connection():
    print("User connected, validating websocket connection")
    server.emit("connection_validated")

# SERVER ROUTING
@web.route('/')
def index():
    return render_template("out-app.html")


def change_frontend_connection():
    global port

    ip_addr = get_ip()
    file_path = os.path.join(os.getcwd(), 'static/framework.js')
    client_server = open(file_path, 'r')
    client_server_lines = client_server.readlines()
    for i, line in enumerate(client_server_lines):
        if line.rstrip().lstrip() == '//$SOCKET_IP':
            client_server_lines[i + 1] = '      socket = io.connect("http://' + ip_addr + ':' + str(
                port) + '"); //This line was autogenerated.\n'
            break

    client_server = open(file_path, 'w')
    client_server.writelines(client_server_lines)
    client_server.close()


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("1.1.1.1", 80))
    ip_addr = s.getsockname()[0]
    s.close()
    return ip_addr


def start():
    global port

    change_frontend_connection()
    if config.DEBUG:
        compiler.start()

    connection_url = 'http://' + get_ip() + ':' + str(port)
    print("Server started at ip: %s" % (connection_url))

    if config.DEBUG:
        pass
        #print("Launching chrome")
        #os.popen("google-chrome " + connection_url)

    server.run(web, host='0.0.0.0', port=port)
