#!/usr/bin/env python
import re
import requests

from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from flask import Flask, Config
from flask import render_template, flash, redirect

from forms import RecordForm

class RecordManagerServer(Flask):
    def __init__(self, *args, **kwargs):
        super(RecordManagerServer, self).__init__(*args, **kwargs)
        self._channels = []
        self._records = []
        
    @property
    def channels(self):
        """
        Return and cache channel list
        """
        if not self._channels:
            requests.get('http://192.168.1.200:8081/login')
            req = requests.get('http://192.168.1.200:8081/channels/')
            soup = BeautifulSoup(req.text, 'html.parser')
            for channel in soup.find_all('channel'):
                self._channels.append(
                    (
                        channel['id'],
                        channel['name'],
                        channel['group'],
                        channel['adult'],
                        channel['epg_id'],
                    )
                )
            self._channels = sorted(self._channels, key=lambda x: x[1])
        return self._channels
    
    @property
    def records(self):
        """
        Return and cache records list
        """
        if not self._records:
            req = requests.get('http://192.168.1.200:8081/records/')
            soup = BeautifulSoup(req.text, 'html.parser')
            channel_name = re.compile(r'(\[.*\])\s(.*)')
            for record in soup.find_all('record'):
                self._records.append(
                    (
                        channel_name.search(record['name']).group(2),
                        datetime.strptime(record['start'], '%d%m%Y_%H%M%S'),
                        datetime.strptime(record['end'], '%d%m%Y_%H%M%S'),
                        record['status'],
                    )
                )
            self._records = sorted(self._records, key=lambda x: x[0])
        return self._records
                

class DefaultConfig(object):
    """
    Default configuration
    """
    IP = "127.0.0.1"
    PORT = "8081"
    #WTF_CSRF_ENABLED = False
    SECRET_KEY = "Testtesttest"

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
    records = app.records
    return render_template('records.html', records=records)

@app.route('/records/add', methods=('GET', 'POST'))
def records_form():
    """
    Form handling for records
    """
    form = RecordForm()
    form.channel_id.choices = [ (channel[0], channel[1])
        for channel in app.channels ]
    now = datetime.now() + timedelta(hours=2)
    later = now + timedelta(hours=2)
    form.start.description = 'e.g. {}'.format(now.strftime('%d-%m-%Y %H:%M'))
    form.end.description = 'e.g. {}'.format(later.strftime('%d-%m-%Y %H:%M'))
    if form.validate_on_submit():
        flash('Record added')
        return redirect('/records')
    return render_template('records_add.html', form=form)

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
