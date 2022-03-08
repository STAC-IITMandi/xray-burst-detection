
from flask import Flask, render_template

app = Flask('XrayIDapp')

@app.route('/')
def landing_page():
    return render_template('base.html')
