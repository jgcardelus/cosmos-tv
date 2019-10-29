# CosmosTv
System that allows you to control netflix, amazon prime, youtube, and other media systems displaying on a computer from your phone. It allows you to select what to watch, play/pause, skip intro, jump to the next episode and much more. All with a sleek and minimalist style.

## Development stage
The server has been created and we are working now on the HTML page which will display on the phone.

## How to use
Open a terminal in CosmosTv's directory and type
```
python3 run.py
```
This will "compile" the page and start the server. Once the server has started it will display the web direction in a line similar to this:
```
Server started at ip: http://192.168.x.xx:8080
```
which will be located before the following: 
```
WebSocket transport not available. Install eventlet or gevent and gevent-websocket for improved performance.
 * Serving Flask app "cosmostv" (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: off
 * Running on http://0.0.0.0:8080/ (Press CTRL+C to quit)
```

## Requisits
- Python3
- Python packages
  - Selenium
  - Flask
  - Flask-socketio
  - Keyboard
  - Mouse


They can be installed with the following command:
```
pip3 install selenium flask flask-socketio keyboard mouse
```
