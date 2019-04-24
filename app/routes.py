#!/usr/bin/python3

from flask import request, session
from flask import render_template
from flask import Markup, Flask
from app import app

import sys
import os

from .ExperimentModel import validate_pid
from .ExperimentModel import get_sentences

#TODO: what if power goes during the task, resume from the last sentence
app = Flask(__name__)

if __name__ == '__main__':
    app.secret_key = "123"
    app.run()
    session['group_id'] = None
    session['pid'] = None
    session['sentences'] = None




@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])

def login():
    pid = request.form['pid']
    cursor = validate_pid(pid)
    if cursor is not None:
        group_id = cursor['gid'].replace('cwig','')
        instructions = '<u>Instructions</u><br><br>A sentence will be displayed in the subsequent screens.<br>You are required to read the sentence and select (click on) the word/s that \
        you do not understand the meaning of.<br>You are required to select the word even if you guessed the meaning based on the context.'
        str = '<center><font color=\'#383838\'><h2>Complex Word Identification in Hindi Sentences</h2>'\
        '<h4>Principal Investigator: Gayatri Venugopal, Symbiosis Institute of Computer Studies and Research<br><br>'\
        'Co-Investigator: Dr. Dhanya Pramod, Symbiosis Centre for Information Technology<br><br>'\
        'Symbiosis International (Deemed University), Pune, India<br><br>'\
        'Project funded by Symbiosis Centre for Research and Innovation, Symbiosis International (Deemed University)<br><br>'\
        'Ethical approval received from the Internal Ethics Committee, Symbiosis International (Deemed University)</font></h4><br></center><h4>' + instructions + '</h4>'

        return render_template('landing.html', text = Markup('<div align=right><font color=green><b>Welcome (' + group_id + ') ' + cursor['pid'] + '!</b></font></div>' \
        + str + '<br><br><center><input type=button value = "Start Task" size = 20 onClick = "location.assign(\'http://localhost:5000/sentence\')")></center>'))
    return render_template('landing.html', text = Markup('<center><h3>Invalid ID!</h3><br>' + '<input type=button value = "Go Back" size = 20 onClick = "history.go(-1)"></center>'))

@app.route('/sentence')

def sentence():
    #get all the sentences allotted the group
    print(group_id, file=sys.stdout)
    sentences = get_sentences(group_id)
    print(sentences, file=sys.stdout)
    return sentences[0]
