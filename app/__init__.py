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
from .ExperimentModel import sentence_state_exists
from .ExperimentModel import words_state_exists
from .ExperimentModel import store_sentence_state
from .ExperimentModel import store_word_state
from .ExperimentModel import store_words
from .ExperimentModel import get_words
from .ExperimentModel import get_synonyms
from .ExperimentModel import get_root
from .ExperimentModel import store_word_ranks


#TODO: logout to clear the session on all the templates
app = Flask(__name__)

if __name__ == '__main__':
    #for session creation
    app.secret_key = "123"
    app.run(host='0.0.0.0')
    session['group_id'] = None
    session['pid'] = None
    session['sentences'] = None
    session['sentence_no'] = 0
    session['word_sentence_no'] = 0
    session['sentences_complete'] = 0
    session['flag'] = 0 #for indicating whether we are on a new sentence in the word ranking task
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

        instructions = '<div class="card"><div class="card-body">'\
        '<h5 style="font-family:Montserrat, sans-serif;font-weight:500;border-bottom:1px dashed grey;padding:5px;">Instructions</h5>'\
        '<p style="font-family:Montserrat, sans-serif;font-style:bold;font-size:13px;">'\
        '⁞ A sentence will be displayed in the subsequent screens.<br />'\
        '⁞ You are required to read the sentence and select (click on) the word/s that you do not understand the meaning of.<br />'\
        '⁞ You are required to select the word even if you guessed the meaning based on the context.<br />'\
        '⁞ Please note that you cannot go back to a previous sentence/screen.<br /></p></div></div>'

        str1 = '<div><p class="text-center" style="font-family:Montserrat, sans-serif;font-weight:bold;font-size:13px;margin-bottom:0px;margin-top:5px;">'\
        '<br />Principal Investigator: Gayatri Venugopal, Symbiosis Institute of Computer Studies and Research<br /><br />'\
        'Co-Investigator: Dr. Dhanya Pramod, Symbiosis Centre for Information Technology<br /><br />'\
        'Symbiosis International (Deemed University),'\
        'Pune, India<br /><br />'\
        'Project funded by Symbiosis Centre for Research and Innovation, Symbiosis International (Deemed University)<br /><br />'\
        'Ethical approval received from the Internal Ethics Committee, Symbiosis International (Deemed University)<br/><br /></p></div>'\
        + instructions
        #display the header text and the instructions
        return render_template('landing.html', text = Markup('<div align=right><font color=green><b>Welcome<font color="white">' + session['group_id'] + '</font>' + cursor['pid'] + '!</b></font></div>' + str1 + '<br><br><div class="d-block" style="text-align:center;"><button class="btn btn-outline-success btn-sm" type="button" onClick = "location.assign(\'http://localhost:5000/sentence\')">Begin Task</button></div>'\
    '</div>'))
    #display an error message if the participant ID does not exist
    return render_template('landing.html', text = Markup('<center><h3 style="margin-top:20px;">Invalid ID!</h3><br>' + '<div class="d-block" style="text-align:center;"><button class="btn btn-outline-danger btn-sm" value="Go Back" type="button" onClick = "history.go(-1)">Go Back</button></div></center>'))

@app.route('/sentence', methods=['GET', 'POST'])

def sentence():
    """ Display the current sentence.
    """
    #check if we came to the page after the login page
    #if request.referrer.find('login'):
    #check if state exists in the database. If so, update the session variables. Take care of sentences_complete.
    state_info = sentence_state_exists(session['pid'])
    if state_info['state'] == 1:
        session['sentence_no'] = state_info['data']['sentence_number']  #this will be incremented subsequently
        print('referrer: ', request.referrer)
#        if request.referrer.find('login') != -1:
#            #subtract one from the sentence number to view the last sentence again
#            session['sentence_no'] = session['sentence_no'] - 1
#            print('subtracted sentence no to ', session['sentence_no'])
        session['sentence_no'] = session['sentence_no'] - 1
        print('subtracted sentence no to ', session['sentence_no'])
        if state_info['data']['sentences_complete'] != None:
            session['sentences_complete'] = state_info['data']['sentences_complete']


    #retrieve all the sentences allotted the group
    sentences = get_sentences(session['group_id'])
    #update the sentence number and set the sentences_complete flag in the session. 1 indicates that all the sentences have been displayed.
    update_sentence_number()

    if 'sentences_complete' in session and session['sentences_complete'] == 1:
        #display the words task
        return render_template('begin_words_task.html', pid = session['pid'])
    #display the current sentence
    return render_template('sentences.html', sentence = sentences[session['sentence_no']], sentence_number = session['sentence_no']+1, pid = session['pid'])

@app.route('/store_tokens', methods=['POST', 'GET'])

def store_tokens():
    """ Store the words selected by the user and display the next sentence.
    """
    #retrieve the JSON object passed in the request
    jsdata = request.get_json()
    #store the words - pid, sentence_no, list of words
    print(jsdata['words'])
    store_words(session['pid'], jsdata['words'], session['sentence_no'])
    #update the sentence number and set the sentences_complete flag in the session. 1 indicates that all the sentences have been displayed.
    update_sentence_number()
    #############################
    #state_info = sentence_state_exists(session['pid'])
    #if state_info['state'] == 1:
    #        session['sentence_no'] = state_info['data']['sentence_number'] #this will be incremented subsequently
    #        print('sentence_no after updating and storing: ',session['sentence_no'])
    #if state_info['data']['sentences_complete'] != None:
    #        session['sentences_complete'] = state_info['data']['sentences_complete']
    ############################




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
    status = store_sentence_state(session['pid'], session['sentence_no'], sentences_complete)

@app.route('/begin_words_task', methods=['GET', 'POST'])
def begin_words_task():
    """ Display the instructions for the task.
    """
    return render_template('begin_words_task.html')

@app.route('/words', methods=['GET', 'POST'])
def words():
    """ Display the words and its synonyms.
    """
    #restore the state if any
    state = words_state_exists(session['pid'])

    if state['data'] is None:
        session['word_sentence_no'] = 0
        session['word_no'] = 0
        session['word'] = None
        session['flag'] = 1
        print("state is none setting flag to 1")
    else:
        session['word_sentence_no'] = int(state['data']['sentence_number'])
        session['word_no'] = state['data']['word_number']
    #print('getting state session word no: ', session['word_no'])
    #retrieve the words from the database
    words_dict = get_words(session['pid'])
    sentence_words = []
    if words_dict['status'] == 1 and words_dict['data'] != None:
        for key,value in words_dict['data'].items():
            sentence_words.append(value)
    else:
        return render_template('end.html')


    if session['flag'] == 1:
        session['word_no'] = 0
        session['flag'] = 0
    else:
        session['word_no'] += 1
    if request.referrer.find('words') != -1:
        print("Flag", session['flag'])

            #print(session.keys())
        print("Word no. ", session['word_no'], " length: ",len(sentence_words[session['word_sentence_no']]))
        if session['word_no'] >= len(sentence_words[session['word_sentence_no']]):
            session['flag'] = 1
            print("Resetting flag to 1")
            print("Incrementing word ", request.referrer)

    elif request.referrer.find('words') == -1 and state['data'] is None:
        session['word_no'] = 0
        session['word_sentence_no'] = 0
    elif request.referrer.find('words') == -1:
        if session['flag'] == 1:
            session['word_no'] = 0
            session['flag'] = 0
            print('setting flag to 0 HERE')
    #display the word and its synonyms']
    i = 0
    print(sentence_words)
    #print("here")
    #print(session['word_sentence_no'])
    #print(sentence_words[session['word_sentence_no']])
    #print("there")
    #print("session flag: ", session['flag'])
    if 'word_no' in session and sentence_words[session['word_sentence_no']] != 0  and session['word_no'] >= len(sentence_words[session['word_sentence_no']]):
        #increment the word_sentence_no in the session
        session['word_sentence_no'] += 1
        session['word_no'] = 0
        session['flag'] = 1
        print('setting word no to 0 and flag to 1')
        #######################
        status = store_word_state(session['pid'], session['word_sentence_no'], session['word_no'])
        #######################
    elif sentence_words[session['word_sentence_no']] == 0 and session['word_sentence_no']<len(sentence_words[session['word_sentence_no']]):
        while len(sentence_words[session['word_sentence_no']])==0 :
            session['word_sentence_no'] += 1
            session['word_no'] = 0
            session['flag'] = 1
            print('setting flag to 1 here')
            #print("setting flag to 1 and proceeding")
            status = store_word_state(session['pid'], session['word_sentence_no'], session['word_no'])
    if session['word_sentence_no'] >= len(sentence_words):
        #TODO: display the final template and logout
        return render_template('end.html')
    for words in sentence_words[session['word_sentence_no']]:
        #print("Words: ", words)
        #print("i: ", i)
        #print("session word no: ", session['word_no'])
        if words.strip() is '':
            i += 1
            #print('continuing')
            session['word_no'] += 1
            continue
        #check if the script has reached the word to be displayed
        if i == session['word_no']:
            #store this state in the words_state collection
            status = store_word_state(session['pid'], session['word_sentence_no'], session['word_no'])
            session['word_no'] += 1
            #pass the set of the word and its synonyms to the template
            #retrieve the synonyms as a set
            synonyms = get_synonyms(words_dict['data'][session['word_sentence_no']][i])
            if synonyms == None:
                #get the root and retrieve its synonyms
                root = get_root(words_dict['data'][session['word_sentence_no']][i])
                synonyms = get_synonyms(root)
                if synonyms == None:
                    i += 1
                    #print("synonyms is none, continuing")
                    session['word_no'] += 1
                    continue
            synonyms.add(words_dict['data'][session['word_sentence_no']][i])
            if len(synonyms) == 0:
                i += 1
                session['word_no'] += 1
                continue
                #words_copy() #TODO: test if this works
            return render_template('words.html', pid=session['pid'], words = [synonyms])
        i += 1
        #words_copy()
    ##############
    session['word_sentence_no'] += 1
    session['flag'] = 1
    print('setting flag to 1 outside')
    #print("End of function, setting flag to 1")
    #session['word_no'] = 0
    status = store_word_state(session['pid'], session['word_sentence_no'], session['word_no'])
    #words_copy()
    ###############
    return render_template('words.html', pid=session['pid'], words={'Select any option to proceed':[]})

'''
def words_copy():
    """ Display the words and its synonyms.
    """
    #restore the state if any
    state = words_state_exists(session['pid'])

    if state['data'] is None:
        session['word_sentence_no'] = 0
        session['word'] = None
    else:
        session['word_sentence_no'] = int(state['data']['sentence_number'])
        session['word_no'] = state['data']['word_number']

    #retrieve the words from the database
    words_dict = get_words(session['pid'])
    sentence_words = []
    if words_dict['status'] == 1 and words_dict['data'] != None:
        for key,value in words_dict['data'].items():
            sentence_words.append(value)
    else:
        return render_template('end.html')
    if request.referrer.find('words') != -1:
        session['word_no'] += 1
    elif state['data'] is None:
        session['word_no'] = 0
        session['word_sentence_no'] = 0
    #display the word and its synonyms
    i = 0
    print(sentence_words)
    print("here")
    print(session['word_sentence_no'])
    print(sentence_words[session['word_sentence_no']])
    print("there")
    if 'word_no' in session and session['word_no'] >= len(sentence_words[session['word_sentence_no']]):
        #increment the word_sentence_no in the session
        session['word_sentence_no'] += 1
        session['word_no'] = 0
        #######################
        status = store_word_state(session['pid'], session['word_sentence_no'], session['word_no'])
        #######################

        if session['word_sentence_no'] >= len(sentence_words):
            #TODO: display the final template and logout
            return render_template('end.html')
    for words in sentence_words[session['word_sentence_no']]:
        print(words)
        if words.strip() is '':
            i += 1
            print('continuing')
            continue
        #check if the script has reached the word to be displayed
        if i == session['word_no']:
            #store this state in the words_state collection
            status = store_word_state(session['pid'], session['word_sentence_no'], session['word_no'])
            #pass the set of the word and its synonyms to the template
            #retrieve the synonyms as a set
            synonyms = get_synonyms(words_dict['data'][session['word_sentence_no']][i])
            if synonyms == None:
                #get the root and retrieve its synonyms
                root = get_root(words_dict['data'][session['word_sentence_no']][i])
                synonyms = get_synonyms(root)
                if synonyms == None:
                    i += 1
                    continue
            synonyms.add(words_dict['data'][session['word_sentence_no']][i])
            if len(synonyms) == 0:
                i += 1
                continue
                words_copy() #TODO: test if this works
            return render_template('words.html', pid=session['pid'], words = [synonyms])
        i += 1
        #words_copy()
    ##############
    session['word_sentence_no'] += 1
    session['word_no'] = 0
    status = store_word_state(session['pid'], session['word_sentence_no'], session['word_no'])
    words_copy()
    ###############
    return render_template('words.html', pid=session['pid'], words={'Select any option to proceed':[]})
'''

@app.route('/store_ranks', methods=['POST', 'GET'])

def store_ranks():
    """ Store the words and their corresponding ranks
    """
    #retrieve the JSON object passed in the request
    jsdata = request.get_json()
    #store the words - pid, sentence_no, list of words
    print(store_word_ranks(session['pid'], jsdata['words']))
    return json.dumps('Success')

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    """ Clear the session and take the user to the first page.
    """
    session.clear()
    return render_template('index.html')
