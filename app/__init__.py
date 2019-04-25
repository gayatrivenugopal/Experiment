#!/usr/bin/python3

from flask import Flask
from flask import redirect
from flask import request

from flask import request, session
from flask import render_template
from flask import Markup, Flask

import sys
import os
import json

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
    session['sentence_no'] = 0

app.secret_key = "123"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])

def login():
    session['pid'] = request.form['pid']
    cursor = validate_pid(session['pid'])
    if cursor is not None:
        session['group_id'] = cursor['gid'].replace('cwig','')
        instructions = '<u>Instructions</u><br><br>A sentence will be displayed in the subsequent screens.<br>You are required to read the sentence and select (click on) the word/s that \
        you do not understand the meaning of.<br>You are required to select the word even if you guessed the meaning based on the context.<br>'\
        'Please note that you cannot go back to a previous sentence/screen.<br>'
        str = '<center><font color=\'#383838\'><h2>Complex Word Identification in Hindi Sentences</h2>'\
        '<h4>Principal Investigator: Gayatri Venugopal, Symbiosis Institute of Computer Studies and Research<br><br>'\
        'Co-Investigator: Dr. Dhanya Pramod, Symbiosis Centre for Information Technology<br><br>'\
        'Symbiosis International (Deemed University), Pune, India<br><br>'\
        'Project funded by Symbiosis Centre for Research and Innovation, Symbiosis International (Deemed University)<br><br>'\
        'Ethical approval received from the Internal Ethics Committee, Symbiosis International (Deemed University)</font></h4><br></center><h4>' + instructions + '</h4>'

        return render_template('landing.html', text = Markup('<div align=right><font color=green><b>Welcome (' + session['group_id'] + ') ' + cursor['pid'] + '!</b></font></div>' \
        + str + '<br><br><center><input type=button value = "Start Task" size = 20 onClick = "location.assign(\'http://localhost:5000/sentence\')")></center>'))
    return render_template('landing.html', text = Markup('<center><h3>Invalid ID!</h3><br>' + '<input type=button value = "Go Back" size = 20 onClick = "history.go(-1)"></center>'))

@app.route('/sentence', methods=['GET', 'POST'])

def sentence():
    #get all the sentences allotted the group
    print(session['group_id'], file = sys.stdout)
    sentences = get_sentences(session['group_id'])
    sentences_complete = display_sentence()
    if sentences_complete == 1:
        return render_template('words.html', pid = session['pid'])
    return render_template('sentences.html', text = sentences[session['sentence_no']], number = session['sentence_no'], pid = session['pid'])

@app.route('/store_tokens', methods=['POST', 'GET'])

def store_tokens():
    jsdata = request.get_json()
    print('Words saved: ' + jsdata['words'], file = sys.stdout)
    sentences_complete = display_sentence()
    if sentences_complete == 1:
        #return render_template('words.html', pid = session['pid'])
        return json.dumps({'sentence_flag': 0});

    sentences = get_sentences(session['group_id'])
    print('here not complete yet', file = sys.stdout)
    current_sentence = sentences[session['sentence_no']]
    print(current_sentence, file = sys.stdout)
    return json.dumps({'sentence_flag':1, 'text': current_sentence, 'number': session['sentence_no'], 'pid': session['pid']});
    #return render_template('sentences.html', text = 'sdfsdf', number = session['sentence_no'], pid = session['pid'])

def display_sentence():
    if 'sentence_no' not in session and 'sentence_complete' not in session:
        session['sentence_no'] = 0
    elif 'sentence_complete' not in session:
        session['sentence_no'] += 1
        #TODO: store input in the database
    if session['sentence_no'] > 99:
        session['sentence_no'] = -1
        session['sentence_complete'] = 1
        return 1
    else:
        print(session['sentence_no'], file = sys.stdout)
        return 0

@app.route('/words', methods=['GET', 'POST'])
def words():
    #TODO: retrieve the selected words from the database, and pass their synonyms to the view
    return render_template('words.html', pid=session['pid'])
