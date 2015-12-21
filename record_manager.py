#!/usr/bin/env python
from flask import Flask
from flask import render_template

app = Flask(__name__)

@app.route('/')
def index():
    """
    Index page with the list of main links to display
    """
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
