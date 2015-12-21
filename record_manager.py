#!/usr/bin/env python
import requests

from flask import Flask, Config
from flask import render_template

app = Flask(__name__)

class DefaultConfig(object):
    """
    Default configuration
    """
    IP = "127.0.0.1"
    PORT = "8081"

# Initialise configuration
app.config.from_object('record_manager.DefaultConfig')
app.config.from_pyfile('config.cfg')

@app.route('/')
def index():
    """
    Index page with the list of main links to display
    """
    # Check if p2p proxy server is accessible
    req = requests.get('http://{}:{}/stat'.format(
        app.config['IP'], app.config['PORT']))
    ok = bool(req.status_code == 200)
    return render_template('index.html', ok=ok)

@app.route('/channels')
def channels():
    """
    Channels link
    """
    return render_template('channels.html')

@app.route('/records')
def records():
    """
    Records link
    """
    return render_template('records.html')

@app.route('/settings')
def settings():
    """
    Settings link
    """
    return render_template('settings.html')

@app.route('/orig')
def orig():
    return render_template('index_orig.html')

if __name__ == '__main__':
    app.run(debug=True)
