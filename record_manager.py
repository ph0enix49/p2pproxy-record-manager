#!/usr/bin/env python
import requests

from bs4 import BeautifulSoup
from flask import Flask, Config
from flask import render_template

class RecordManagerServer(Flask):
    def __init__(self, *args, **kwargs):
        super(RecordManagerServer, self).__init__(*args, **kwargs)
        self._channels = {}
        
    @property
    def channels(self):
        """
        Return and cache channel list
        """
        if not self._channels:
            req = requests.get('http://192.168.1.200:8081/channels/')
            soup = BeautifulSoup(req.text, 'html.parser')
            self._channels = {}
            for channel in soup.find_all('channel'):
                self._channels[channel['id']] = {
                    'name': channel['name'],
                    'group': channel['group'],
                    'adult': channel['adult'],
                    'epg_id': channel['epg_id'],
                }
        return self._channels
                

class DefaultConfig(object):
    """
    Default configuration
    """
    IP = "127.0.0.1"
    PORT = "8081"

# Initialise application
app = RecordManagerServer(__name__)

# Initialise configuration
app.config.from_object('record_manager.DefaultConfig')
app.config.from_pyfile('config.cfg')

@app.route('/')
def index():
    """
    Index page with the list of main links to display
    """
    # Check if p2p proxy server is accessible
    try:
        req = requests.get('http://{}:{}/stat'.format(
            app.config['IP'], app.config['PORT']), timeout=2)
        ok = bool(req.status_code == 200)
    except:
        ok = False
    return render_template('index.html', ok=ok)

@app.route('/channels')
def channels():
    """
    Channels link
    """
    channels = app.channels
    return render_template('channels.html', channels=channels)
    

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
