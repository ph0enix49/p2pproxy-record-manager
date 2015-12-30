#!/usr/bin/env python

import argparse
import re
import requests
import random

from collections import OrderedDict
from string import Template, ascii_letters
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from flask import Flask, Config, g
from flask import render_template, flash, redirect, request

from forms import RecordForm

class RecordManagerServer(Flask):
    def __init__(self, *args, **kwargs):
        super(RecordManagerServer, self).__init__(*args, **kwargs)
        self._channels = OrderedDict()
        
    def generate_url(self, ip, port):
        """
        Generate a URL
        """
        self.url = Template('http://{}:{}/$target'.format(ip, port))
        
    @property
    def channels(self):
        """
        Return and cache channel list.
        """
        if not self._channels or len(self._channels) == 0:
            requests.get(self.url.substitute(target='login'), timeout=5)
            req = requests.get(self.url.substitute(target='channels/'),
                timeout=2)
            soup = BeautifulSoup(req.text, 'html.parser')
            groups = { group['id']: group['name']
                      for group in soup.find_all('category') }
            for channel in soup.find_all('channel'):
                self._channels[channel['id']] = {
                        'name': channel['name'],
                        'group': groups[channel['group']],
                        'adult': channel['adult'],
                        'epg': channel['epg_id'],
                }
        return self._channels
    
    @property
    def records(self):
        """
        Return and cache recordings list.
        """
        requests.get(self.url.substitute(target='login'), timeout=2)
        req = requests.get(self.url.substitute(target='records/all'),
            timeout=2)
        soup = BeautifulSoup(req.text, 'html.parser')
        channel_name = re.compile(r'(\[.*\])\s(.*)')
        records = []
        for record in soup.find_all('record'):
            records.append(
                (
                    channel_name.search(record['name']).group(2),
                    datetime.strptime(record['start'], '%d%m%Y_%H%M%S'),
                    datetime.strptime(record['end'], '%d%m%Y_%H%M%S'),
                    record['status'],
                    record['id'],
                )
            )
        return sorted(records, key=lambda x: x[0])
    
    def disable_links(self):
        """
        Disable links when P2P proxy is inaccessible.
        """
        try:
            req = requests.get(app.url.substitute(target='stat'), timeout=2)
            ok = bool(req.status_code == 200)
        except:
            ok = False
        if not ok:
            disabled = ['channels', 'records']
        else:
            disabled = []
        return ok, disabled
                

class DefaultConfig(object):
    """
    Default configuration.
    """
    random = random.SystemRandom()
    IP = "127.0.0.1"
    PORT = "8081"
    SECRET_KEY = ''.join(random.choice(ascii_letters) for _ in range(15))

# Initialise application
app = RecordManagerServer(__name__)

# Initialise configuration
app.config.from_object(DefaultConfig)

@app.route('/')
def index():
    """
    Index page with the list of main links to display.
    """
    # Check if p2p proxy server is accessible
    ok, disabled = app.disable_links()
    status_params = (app.config['IP'], app.config['PORT'])
    return render_template('index.html', ok=ok, disabled=disabled,
                           status_params=status_params)

@app.route('/channels')
def channels():
    """
    Channels list view.
    """
    return render_template('channels.html', channels=app.channels)
    
@app.route('/channels/<channel_id>')
def channel_view(channel_id):
    """
    Channel detail view.
    """
    channel = app.channels[channel_id]
    try:
        payload = {
            'id': channel['epg'],
        }
        requests.get(app.url.substitute(target='login'), timeout=2)
        req = requests.get(app.url.substitute(
            target='epg/'), params=payload, timeout=2)
        soup = BeautifulSoup(req.text, 'html.parser')
        epgs = []
        for epg in soup.find_all('telecast'):
            epgs.append(
                (
                    datetime.fromtimestamp(float(epg['btime'])),
                    datetime.fromtimestamp(float(epg['etime'])),
                    epg['name'],
                )
            )
    except Exception as e:
        flash('Channel view failed: {}'.format(e), 'error')
    return render_template('channel_view.html', channel=channel,
                           channel_id=channel_id, epgs=epgs)

@app.route('/records')
def records():
    """
    Recordings list view.
    """
    records = app.records
    return render_template('records.html', records=records)


@app.route('/records/add/<channel_id>/<btime>/<etime>', methods=('GET', 'POST'))
@app.route('/records/add', methods=('GET', 'POST'))
def records_form(channel_id=None, btime=None, etime=None):
    """
    Form handling for recordings.
    """
    form = RecordForm()
    form.channel_id.choices = [ (int(id), channel['name'])
        for id, channel in app.channels.items() ]
    if channel_id and btime and etime:
        try:
            btime = datetime.strptime(btime, '%Y-%m-%d %H:%M:%S')
            etime = datetime.strptime(etime, '%Y-%m-%d %H:%M:%S')
            form.channel_id.data = int(channel_id)
            form.start.data = btime
            form.end.data = etime
        except ValueError:
            flash('Datetime arguments are invalid: {}'.format(e), 'error')
            return redirect('/records')
    now = datetime.now() + timedelta(hours=2)
    later = now + timedelta(hours=2)
    form.start.description = 'e.g. {}'.format(now.strftime('%d-%m-%Y %H:%M'))
    form.end.description = 'e.g. {}'.format(later.strftime('%d-%m-%Y %H:%M'))
    if form.validate_on_submit():
        try:
            payload = {
                'channel_id': form.channel_id.data,
                'start': form.start.data.strftime('%d%m%Y_%H%M%S'),
                'end': form.end.data.strftime('%d%m%Y_%H%M%S'),
            }
            requests.get(app.url.substitute(target='login'), timeout=2)
            result = requests.get(app.url.substitute(
                target='records/add'), params=payload, timeout=2)
            flash('Record scheduled', 'success')
        except Exception as e:
            flash('Record schedule failed: {}'.format(e), 'error')
        return redirect('/records')
    return render_template('records_add.html', form=form)


@app.route('/records/delete/<record_id>')
def records_delete_confirmation(record_id):
    """
    Confirm and delete recordings.
    """
    try:
        payload = {
            'id': record_id,
        }
        stop = requests.get(app.url.substitute(
            target='records/del'), params=payload, timeout=2)
        delete = requests.get(app.url.substitute(
            target='records/del'), params=payload, timeout=2)
        if delete.status_code != 200:
            raise Exception('delete failed')
        if stop.status_code != 200:
            raise Exception('stop failed')
        flash('Record deleted', 'success')
    except Exception as e:
        flash('Record deletion failed: {}'.format(e), 'error')
    return redirect('/records')


def main():
    """
    Main function to execute.
    """
    parser = argparse.ArgumentParser(description=(
        'P2P Proxy Record manager. Manage P2P proxy recordings.'
        )
    )
    parser.add_argument('--p2pproxy-address', '-a', default='127.0.0.1',
        help='P2P Proxy IP address. Default: 127.0.0.1')
    parser.add_argument('--p2pproxy-port', '-p', default='8081',
        help='P2P Proxy port. Default: 8081')
    parser.add_argument('--version', action='version', version='%(prog)s 0.1')
    args = parser.parse_args()
    app.config['IP'] = args.p2pproxy_address
    app.config['PORT'] = args.p2pproxy_port
    app.generate_url(app.config['IP'], app.config['PORT'])
    app.run(host='0.0.0.0')

if __name__ == '__main__':
    main()
