#!/usr/bin/python3

from flask import request
from flask import render_template
from flask import Markup
from app import app

from .ExperimentModel import validate_pid

group_id = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=["GET", "POST"])

def login():
    pid = request.form['pid']
    cursor = validate_pid(pid)
    if cursor is not None:
        group_id = cursor['gid']
        str = '<center><font color=\'#383838\'><h2>Complex Word Identification in Hindi Sentences</h2>'\
        '<h4>Principal Investigator: Gayatri Venugopal, Symbiosis Institute of Computer Studies and Research<br><br>'\
        'Co-Investigator: Dr. Dhanya Pramod, Symbiosis Centre for Information Technology<br><br>'\
        'Symbiosis International (Deemed University), Pune, India<br><br>'\
        'Project funded by Symbiosis Centre for Research and Innovation, Symbiosis International (Deemed University)<br><br>'\
        'Ethical approval received from the Internal Ethics Committee, Symbiosis International (Deemed University)</font></h4></center>'
        return render_template('landing.html', text = Markup('<div align=right><font color=green><b>Welcome (' + group_id + ') ' + cursor['pid'] + '!</b></font></div>' + str))
    return render_template('landing.html', text = Markup('<center><h3>Invalid ID!</h3><br>' + '<input type=button value = "Go Back" size = 20 onClick = "history.go(-1)"></center>'))
