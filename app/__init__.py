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
    #for indicating whether we are on a new sentence in the word ranking task

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
        '<p style="font-family:Montserrat, sans-serif;font-style:bold;font-size:14px;">'\
        '⁞ A sentence will be displayed in the subsequent screens.<br />'\
        '⁞ You are required to read the sentence and select (click on) the word/s if you are not aware of the meaning of the word.<br />'\
        '⁞ You are required to select the word even if you guessed the meaning based on the context.<br />'\
        '⁞ The navigation could be slow, please <b>do not click the Next button more than once</b>.<br />'\
        '⁞ Please note that you cannot go back to a previous sentence/screen.<br /></p></div></div>'

        str1 = '<div><p class="text-center" style="font-family:Montserrat, sans-serif;font-weight:bold;font-size:13px;margin-bottom:0px;margin-top:5px;">'\
        '<br />Principal Investigator: Gayatri Venugopal, Symbiosis Institute of Computer Studies and Research<br /><br />'\
        'Co-Investigator: Dr. Dhanya Pramod, Symbiosis Centre for Information Technology<br /><br />'\
        'Symbiosis International (Deemed University),'\
        'Pune, India<br /><br />'\
        'Project funded by Symbiosis Centre for Research and Innovation, Symbiosis International (Deemed University)<br /><br />'\
        'Ethical approval received from the Internal Ethics Committee, Symbiosis International (Deemed University)<br/><br /></p></div>'\
        + instructions
        f = open(session['pid']+'session.txt','w')
        f.write('0')
        f.close()
        f = open(session['pid']+'flag.txt','w')
        f.write('0')
        f.close()
        f = open(session['pid']+'sentences.txt','w')
        f.write('')
        f.close()
        f = open(session['pid']+'sentence_no.txt','w')
        f.write('0')
        f.close()
        f = open(session['pid']+'word_sentence_no.txt','w')
        f.write('0')
        f.close()
        f = open(session['pid']+'sentences_complete.txt','w')
        f.write('0')
        f.close()

        #display the header text and the instructions
        return render_template('landing.html', text = Markup('<div align=right><font color=green><b>Welcome<font color="white">' + session['group_id'] + '</font>' + cursor['pid'] + '!</b></font></div>' + str1 + '<br><br><div class="d-block" style="text-align:center;"><button class="btn btn-outline-success btn-sm" type="button" onClick = "location.assign(\'http://107.191.96.150:5000/sentence\')">Begin Task</button></div>'\
    '</div>'))
    #display an error message if the participant ID does not exist
    return render_template('landing.html', text = Markup('<center><h3 style="margin-top:20px;">Invalid ID!</h3><br>' + '<div class="d-block" style="text-align:center;"><button class="btn btn-outline-danger btn-sm" value="Go Back" type="button" onClick = "history.go(-1)">Go Back</button></div></center>'))

@app.route('/sentence', methods=['GET', 'POST'])

def sentence():
    """ Display the current sentence.
    """
    #check if we came to the page after the login page
    #check if state exists in the database. If so, update the session variables. Take care of sentences_complete.
    state_info = sentence_state_exists(session['pid'])
    tempf = open(session['pid']+'session.txt', 'r')
    tempvalue = tempf.read()
    tempf.close()
    if state_info['state'] == 1:
        #session['sentence_no'] = state_info['data']['sentence_number']  #this will be incremented subsequently
        f = open(session['pid']+'sentence_no.txt','w')
        f.write(str(state_info['data']['sentence_number']))
        f.close()
        if request.referrer.find('login') != -1:# or open(session['pid']+'session.txt', 'r').read().strip() == '1':
            #subtract one from the sentence number to view the last sentence again
            #session['sentence_no'] = session['sentence_no'] - 1
#            temp = int(open(session['pid']+'sentence_no.txt','r').read().strip())
#            open(session['pid']+'sentence_no.txt','w').write(str(temp-1))
            f = open(session['pid']+'sentence_no.txt','r')
            temp = f.read()
            f.close()
            if int(temp) != 0:
                f = open(session['pid']+'sentence_no.txt','r')
                temp = f.read()
                f.close()
                f = open(session['pid']+'sentence_no.txt','w')
                f.write(str(int(temp)-1))
                f.close()


        if state_info['data']['sentences_complete'] != None:
            #session['sentences_complete'] = state_info['data']['sentences_complete']
	        f = open(session['pid']+'sentences_complete.txt','w')
	        f.write(str(state_info['data']['sentences_complete']))
	        f.close()
    elif request.referrer.find('login') != -1 or tempvalue == '1':
        f = open(session['pid']+'sentence_no.txt','r')
        temp = f.read()
        f.close()
        f = open(session['pid']+'sentence_no.txt','w')
        f.write(str(int(temp)-1))
        f.close()

        f = open(session['pid']+'session.txt','w')
        f.write('0')
        f.close()

    #retrieve all the sentences allotted the group
    sentences = get_sentences(session['group_id'])
    #update the sentence number and set the sentences_complete flag in the session. 1 indicates that all the sentences have been displayed.

    update_sentence_number()

    #if 'sentences_complete' in session and session['sentences_complete'] == 1:
    #if session['sentences_complete'] == 1:
    f = open(session['pid']+'sentences_complete.txt','r')
    temp = f.read()
    f.close()
    if temp == '1':
        #display the words task
        return render_template('begin_words_task.html', pid = session['pid'])
    #display the current sentence
    #return render_template('sentences.html', sentence = sentences[session['sentence_no']], sentence_number = session['sentence_no']+1, pid = session['pid'])
    f1 = open(session['pid']+'sentence_no.txt','r')
    temp1 = f1.read()
    f1.close()
    f2 = open(session['pid']+'sentence_no.txt','r')
    temp2 = f2.read()
    f2.close()
    return render_template('sentences.html', sentence = sentences[int(temp1)], sentence_number = int(temp2)+1, pid = session['pid'])

@app.route('/store_tokens', methods=['POST'])

def store_tokens():
    """ Store the words selected by the user and display the next sentence.
    """
    #retrieve the JSON object passed in the request
    jsdata = request.get_json()
    #store the words - pid, sentence_no, list of words
    if len(jsdata['words']) != 0:
        f = open(session['pid']+'session.txt', 'w')
        f.write('1')
        f.close()
    #store_words(session['pid'], jsdata['words'], session['sentence_no'])
    f = open(session['pid']+'sentence_no.txt','r')
    temp = f.read()
    f.close()
    store_words(session['pid'], jsdata['words'], temp)
    #update the sentence number and set the sentences_complete flag in the session. 1 indicates that all the sentences have been displayed.



#    update_sentence_number()

    #if 'sentences_complete' in session and session['sentences_complete'] == 1:
    f = open(session['pid']+'sentences_complete.txt','r')
    temp = f.read()
    f.close()
    if int(temp) == 1:
        #return the flag
        return json.dumps({'sentence_flag': 0});
    #retrieve all the sentences allotted to the group
    sentences = get_sentences(session['group_id'])
    #return the flag, the current sentence, the sentence number and the participant ID
    #return json.dumps({'sentence_flag':1, 'sentence': sentences[session['sentence_no']], 'sentence_number': session['sentence_no']+1, 'pid': session['pid']});
    f = open(session['pid']+'sentence_no.txt','r')
    temp = f.read()
    f.close()
    f = open(session['pid']+'sentence_no.txt','r')
    temp2 = f.read()
    f.close()
    return json.dumps({'sentence_flag':1, 'sentence': sentences[int(temp)], 'sentence_number': int(temp2)+1, 'pid': session['pid']})

def update_sentence_number():
    """ Update the current sentence number.
    """
    #initialize sentence_no in the session
    #if 'sentence_no' not in session and 'sentences_complete' not in session:
    #        session['sentence_no'] = 0

    #otherwise, increment the sentence_no if it is present in the session
    sentences_complete = 0
    #elif 'sentences_complete' not in session:
    f = open(session['pid']+'sentences_complete.txt','r')
    temp = f.read()
    f.close()
    if int(temp) == 0:# and int(open(session['pid']+'sentence_no.txt','r').read().strip())!=0:
        #session['sentence_no'] += 1
        f = open(session['pid']+'sentence_no.txt','r')
        temp = f.read()
        f.close()
        f = open(session['pid']+'sentence_no.txt','w')
        f.write(str(int(temp)+1))
        f.close()
    #set the flag in the session if the sentence_no exceeds 99 (beginning from 0)
    #if session['sentence_no'] > 99:
    f = open(session['pid']+'sentence_no.txt','r')
    temp = f.read()
    f.close()

    filetemp = open(session['pid']+'sentences_complete.txt','r')
    tempvalue = filetemp.read()
    filetemp.close()
    if int(temp) > 99:
        f = open(session['pid'] + 'sentences_complete.txt', 'w')
        f.write('1')
        f.close()
        #session['sentences_complete'] = 1
    if int(tempvalue) != 0:
        #sentences_complete = session['sentences_complete']
        f = open(session['pid']+'sentences_complete.txt','r')
        temp = f.read()
        f.close()
        sentences_complete = int(temp)
    #status = store_sentence_state(session['pid'], session['sentence_no'], sentences_complete)
    f = open(session['pid']+'sentence_no.txt','r')
    temp = f.read()
    f.close()
    status = store_sentence_state(session['pid'], temp, sentences_complete)

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
        #session['word_sentence_no'] = 0
        f = open(session['pid']+'word_sentence_no.txt','w')
        f.write('0')
        f.close()
        #session['word_no'] = 0
        f = open(session['pid']+'word_no.txt','w')
        f.write('0')
        f.close()
        #session['word'] = None
        f = open(session['pid']+'word.txt','w')
        f.write('')
        f.close()
        #session['flag'] = 1
        f = open(session['pid']+'flag.txt', 'w')
        f.write('1')
        f.close()
    else:
        #session['word_sentence_no'] = int(state['data']['sentence_number'])
        f = open(session['pid']+'word_sentence_no.txt','w')
        f.write(str(int(state['data']['sentence_number'])))
        f.close()
        #session['word_no'] = state['data']['word_number']
        f = open(session['pid']+'word_no.txt','w')
        f.write(str(int(state['data']['word_number'])))
        f.close()
    #retrieve the words from the database
    words_dict = get_words(session['pid'])
    print('words dict ', words_dict)
    sentence_words = []
    if words_dict['status'] == 1 and words_dict['data'] != None:
        #i = 0
        print("length of word dict data items ", len(words_dict['data'].items()))
        for key,value in words_dict['data'].items():
            sentence_words.append(value)
            #print(i)
            #input()
            #i+= 1
    else:
        return render_template('end.html')
    print(sentence_words)
    print(len(sentence_words))
    ##############
    #return ''
    ############
    if len(sentence_words) == 0:
        #session['word_sentence_no'] += 1
        f = open(session['pid']+'word_sentence_no.txt','w')
        f2 = open(session['pid']+'word_sentence_no.txt','r')
        temp = f2.read()
        f2.close()
        f.write(str(int(temp) + 1))
        f.close()
        f = open(session['pid']+'flag.txt','w')
        f.write('1')
        f.close()
        #session['word_no'] = 0
        #status = store_word_state(session['pid'], session['word_sentence_no'], session['word_no'])
        f = open(session['pid']+'word_sentence_no.txt','r')
        temp = f.read()
        f.close()
        f = open(session['pid']+'word_no.txt','r')
        temp2 = f.read()
        f.close()
        status = store_word_state(session['pid'], int(temp), int(temp2))
        #if session['word_sentence_no'] >= len(sentence_words):
        f = open(session['pid']+'word_sentence_no.txt','r')
        temp = f.read()
        f.close()
        if int(temp) >= len(sentence_words):
            return render_template('end.html')
        return render_template('words.html', pid=session['pid'], words={'Select any option to proceed':[]})
    f = open(session['pid']+'flag.txt','r')
    temp = f.read()
    f.close()
    if temp == '1':
        #session['word_no'] = 0
        f = open(session['pid']+'word_no.txt','w')
        f.write('0')
        f.close()
        #session['flag'] = 0
        f = open(session['pid']+'flag.txt','w')
        f.write('0')
        f.close()
    else:
        #session['word_no'] += 1
        f = open(session['pid']+'word_sentence_no.txt','r')
        temp = f.read()
        f.close()
        f = open(session['pid']+'word_sentence_no.txt','w')
        f.write(str(int(temp) + 1))
        f.close()
    if request.referrer.find('words') != -1:
        #if session['word_no'] >= len(sentence_words[session['word_sentence_no']]):
        f = open(session['pid']+'word_sentence_no.txt','r')
        temp = f.read()
        f.close()
        f = open(session['pid']+'word_no.txt','r')
        temp2 = f.read()
        f.close()
        print("temp: ",temp)
        print("sentence words: ", sentence_words)
        if int(temp) >= len(sentence_words):
            return render_template('end.html')
        if int(temp2) >= len(sentence_words[int(temp)]):
	        f = open(session['pid']+'flag.txt','w')
	        f.write('1')
	        f.close()

    elif request.referrer.find('words') == -1 and state['data'] is None:
        #session['word_no'] = 0
        session['word_no'] = 0
        f = open(session['pid']+'word_no.txt','w')
        f.write('0')
        f.close()
        #session['word_sentence_no'] = 0
        f = open(session['pid']+'word_sentence_no.txt','w')
        f.write('0')
        f.close()
    elif request.referrer.find('words') == -1:
        f = open(session['pid']+'flag.txt','r')
        temp = f.read()
        f.close()
        if temp == '1':
            #session['word_no'] = 0
            f = open(session['pid']+'word_no.txt','w')
            f.write('0')
            f.close()
            f = open(session['pid']+'flag.txt','w')
            f.write('0')
            f.close()

    i = 0

    f = open(session['pid']+'word_sentence_no.txt','r')
    temp1 = f.read()
    f.close()
    f = open(session['pid']+'word_no.txt','r')
    temp2 = f.read()
    f.close()
    f = open(session['pid']+'word_sentence_no.txt','r')
    temp3 = f.read()
    f.close()
    f = open(session['pid']+'word_sentence_no.txt','r')
    temp4 = f.read()
    f.close()
    print("sentence words: ", sentence_words)
    print("temp1 and temp3: ", temp1)
    #return ''
        
    #if 'word_no' in session and sentence_words[session['word_sentence_no']] != 0  and session['word_no'] >= len(sentence_words[session['word_sentence_no']]):
    if len(sentence_words[int(temp1)]) != 0  and int(temp2) >= len(sentence_words[int(temp3)]):
        #increment the word_sentence_no in the session
        #session['word_sentence_no'] += 1
        f = open(session['pid']+'word_sentence_no.txt','r')
        temp = f.read()
        f.close()
        f = open(session['pid']+'word_sentence_no.txt','w')
        f.write(str(int(temp)+1))
        f.close()
        #session['word_no'] = 0
        f = open(session['pid']+'word_no.txt','w')
        f.write('0')
        f.close()
        f = open(session['pid']+'flag.txt','w')
        f.write('1')
        f.close()
        #######################
        #status = store_word_state(session['pid'], session['word_sentence_no'], session['word_no'])
        f = open(session['pid']+'word_sentence_no.txt','r')
        temp1 = f.read()
        f.close()
        f = open(session['pid']+'word_no.txt','r')
        temp2 = f.read()
        f.close()
        status = store_word_state(session['pid'], int(temp1),int(temp2))
        #######################
    #elif sentence_words[session['word_sentence_no']] == 0 and session['word_sentence_no']<len(sentence_words[session['word_sentence_no']]):
    elif len(sentence_words[int(temp4)]) == 0 and int(temp4)<len(sentence_words[int(temp4)]):
        #while len(sentence_words[session['word_sentence_no']])==0 :
        f = open(session['pid']+'word_sentence_no.txt','r')
        t = f.read()
        f.close()
        while len(sentence_words[int(t)])==0:

            #session['word_sentence_no'] += 1
            f = open(session['pid']+'word_sentence_no.txt','r')
            temp = f.read()
            f.close()
            f = open(session['pid']+'word_sentence_no.txt','w')
            f.write(str(int(temp) + 1))
            f.close()
            #session['word_no'] = 0
            f = open(session['pid']+'word_no.txt','w')
            f.write('0')
            f.close()
            f = open(session['pid']+'flag.txt','w')
            f.write('1')
            f.close()
            #status = store_word_state(session['pid'], session['word_sentence_no'], session['word_no'])
            f = open(session['pid']+'word_sentence_no.txt','r')
            temp1 = f.read()
            f.close()
            f = open(session['pid']+'word_no.txt','r')
            temp2 = f.read()
            f.close()
            status = store_word_state(session['pid'], int(temp1), int(temp2))
    #if session['word_sentence_no'] >= len(sentence_words):
    f = open(session['pid']+'word_sentence_no.txt','r')
    temp = f.read()
    f.close()
    if int(temp) >= len(sentence_words):
        #TODO: display the final template and logout
        return render_template('end.html')
    #for words in sentence_words[session['word_sentence_no']]:
    f = open(session['pid']+'word_sentence_no.txt','r')
    temp = f.read()
    f.close()
    for words in sentence_words[int(temp)]:
        print("words: ", words)
        f = open(session['pid']+'word_no.txt','r')
        t = f.read()
        f.close()
        if words.strip() is '':
            i += 1
            #session['word_no'] += 1
            f = open(session['pid']+'word_no.txt','r')
            temp = f.read()
            f.close()
            f = open(session['pid']+'word_no.txt','w')
            f.write(str(int(temp) + 1))
            f.close()
            print("continuing 1")
            continue
        #check if the script has reached the word to be displayed
        #if i == session['word_no']:
        if i == int(t):
            #store this state in the words_state collection
            #status = store_word_state(session['pid'], session['word_sentence_no'], session['word_no'])
            f = open(session['pid']+'word_sentence_no.txt','r')
            temp1 = f.read()
            f.close()
            f = open(session['pid']+'word_no.txt','r')
            temp2 = f.read()
            f.close()
            status = store_word_state(session['pid'], int(temp1), int(temp2))
            #session['word_no'] += 1
            f = open(session['pid']+'word_no.txt','r')
            temp = f.read()
            f.close()
            f = open(session['pid']+'word_no.txt','w')
            f.write(str(int(temp) + 1))
            f.close()
            #pass the set of the word and its synonyms to the template
            #retrieve the synonyms as a set
            synonyms = get_synonyms(words)#words_dict['data'][session['word_sentence_no']][i])
            if synonyms == None:
                #get the root and retrieve its synonyms
                root = get_root(words)#_dict['data'][session['word_sentence_no']][i])
                synonyms = get_synonyms(root)
                if synonyms == None:
                    i += 1
                    #session['word_no'] += 1
                    f = open(session['pid']+'word_no.txt','r')
                    temp = open(session['pid']+'word_no.txt','r').read()
                    f.close()
                    f = open(session['pid']+'word_no.txt','w')
                    f.write(str(int(temp) + 1))
                    f.close()
                    print("continuing 2")
                    continue
            synonyms.add(words)#_dict['data'][session['word_sentence_no']][i])
            if len(synonyms) == 0:
                i += 1
                #session['word_no'] += 1
                f = open(session['pid']+'word_no.txt','r')
                temp = f.read()
                f.close()
                f = open(session['pid']+'word_no.txt','w')
                f.write(str(int(temp) + 1))
                f.close()
                print("continuing 3")
                continue
                print("HERE")
            return render_template('words.html', pid=session['pid'], words = [synonyms])
        i += 1
    ##############
    #session['word_sentence_no'] += 1
    f = open(session['pid']+'word_sentence_no.txt','r')
    temp = f.read()
    f.close()
    f = open(session['pid']+'word_sentence_no.txt','w')
    f.write(str(int(temp) + 1))
    f.close()

    f = open(session['pid']+'flag.txt','w')
    f.write('1')
    f.close()
    #session['word_no'] = 0
    #status = store_word_state(session['pid'], session['word_sentence_no'], session['word_no'])
    f = open(session['pid']+'word_sentence_no.txt','r')
    temp1 = f.read()
    f.close()
    f = open(session['pid']+'word_no.txt','r')
    temp2 = f.read()
    f.close()
    status = store_word_state(session['pid'], int(temp1), int(temp2))
    ###############
    return render_template('words.html', pid=session['pid'], words={'Select any option to proceed':[]})

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
