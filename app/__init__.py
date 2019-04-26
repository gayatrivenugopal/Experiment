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
from .ExperimentModel import state_exists
from .ExperimentModel import store_state


#TODO: what if power goes during the task, resume from the last sentence
#TODO: logout to clear the session on all the templates
app = Flask(__name__)

if __name__ == '__main__':
    #for session creation
    app.secret_key = "123"
    app.run()
    session['group_id'] = None
    session['pid'] = None
    session['sentences'] = None
    session['sentence_no'] = 0
    session['sentences_complete'] = 0

app.secret_key = "123"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])

def login():
    """ login and display the instructions, or display an error message in case
    the participant ID does not exist in the database.
    """
    #retrieve the participant ID and store in the session
    session['pid'] = request.form['pid']

    #check if the participant ID exists
    cursor = validate_pid(session['pid'])
    if cursor is not None:
        #store the group number in the session
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
        #display the header text and the instructions
        return render_template('landing.html', text = Markup('<div align=right><font color=green><b>Welcome (' + session['group_id'] + ') ' + cursor['pid'] + '!</b></font></div>' \
        + str + '<br><br><center><input type=button value = "Start Task" size = 20 onClick = "location.assign(\'http://localhost:5000/sentence\')")></center>'))
    #display an error message if the participant ID does not exist
    return render_template('landing.html', text = Markup('<center><h3>Invalid ID!</h3><br>' + '<input type=button value = "Go Back" size = 20 onClick = "history.go(-1)"></center>'))

@app.route('/sentence', methods=['GET', 'POST'])

def sentence():
    """ Display the current sentence.
    """
    #check if we came to the page after the login page
    if request.referrer.find('login'):
        #check if state exists in the database. If so, update the session variables. Take care of sentences_complete.
        state_info = state_exists(session['pid'])
        print(state_info, file = sys.stdout)
        if state_info['state'] == 1:
            session['sentence_no'] = state_info['data']['sentence_number'] -1 #this will be incremented subsequently
            if state_info['data']['sentences_complete'] != None:
                session['sentences_complete'] = state_info['data']['sentences_complete']

    #retrieve all the sentences allotted the group
    sentences = get_sentences(session['group_id'])
    #update the sentence number and set the sentences_complete flag in the session. 1 indicates that all the sentences have been displayed.
    update_sentence_number()
    if 'sentences_complete' in session and session['sentences_complete'] == 1:
        #display the words task
        return render_template('words.html', pid = session['pid'])
    #display the current sentence
    return render_template('sentences.html', sentence = sentences[session['sentence_no']], sentence_number = session['sentence_no']+1, pid = session['pid'])

@app.route('/store_tokens', methods=['POST', 'GET'])

def store_tokens():
    """ Store the words selected by the user and display the next sentence.
    """
    #retrieve the JSON object passed in the request
    jsdata = request.get_json()
    #TODO: store the words
    print('Words saved: ' + jsdata['words'], file = sys.stdout)
    #update the sentence number and set the sentences_complete flag in the session. 1 indicates that all the sentences have been displayed.
    update_sentence_number()
    if 'sentences_complete' in session and session['sentences_complete'] == 1:
        #return the flag
        return json.dumps({'sentence_flag': 0});
    #retrieve all the sentences allotted to the group
    sentences = get_sentences(session['group_id'])
    #return the flag, the current sentence, the sentence number and the participant ID
    return json.dumps({'sentence_flag':1, 'sentence': sentences[session['sentence_no']], 'sentence_number': session['sentence_no']+1, 'pid': session['pid']});

def update_sentence_number():
    """ Update the current sentence number.
    """
    #initialize sentence_no in the session
    if 'sentence_no' not in session and 'sentences_complete' not in session:
        session['sentence_no'] = 0
    #otherwise, increment the sentence_no if it is present in the session
    elif 'sentences_complete' not in session:
        session['sentence_no'] += 1
    #set the flag in the session if the sentence_no exceeds 99 (beginning from 0)
    if session['sentence_no'] > 99:
        session['sentences_complete'] = 1
    #store the participant ID, the sentence number and the sentences_complete flag in the database
    if 'sentences_complete' not in session:
        sentences_complete = None
    else:
        sentences_complete = session['sentences_complete']
    status = store_state(session['pid'], session['sentence_no'], sentences_complete)
    print(status, file = sys.stdout)

@app.route('/words', methods=['GET', 'POST'])
def words():
    """ Display the word and its synonyms.
    """
    #TODO: retrieve the selected words from the database, and pass their synonyms to the view
    return render_template('words.html', pid=session['pid'])
