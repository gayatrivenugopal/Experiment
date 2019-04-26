#!/usr/bin/python3
from pymongo import MongoClient

#connect to the MongoDB instance
client = MongoClient('localhost:27017')
database = client.Experiment

def validate_pid(pid):
    results = document_exists('Groups', 'pid', pid)
    if results['status'] == 1 and results['data'] != 0:
        return results['data']

def document_exists(collection, field, value):
    """ Checks whether the document consisting of a particular value in the
    specific field exists

    Args:
        collection (str): the collection that is to be queried
        field (str): the field whose value is to be checked
        value (str): the value that is to be checked

    Returns:
        (dict): the status which is 1, if successful and -1, if unsuccessful,
        and the data to be sent back, in this case, 1, if the document exists,
        0, if the document does not exist, or the description of the error, if
        any.
    """
    #print("Collection: ", collection, " Field: ", field, " Value: ", value)
    try:
        cursor = database[collection].find_one({field: value})
        if cursor is None:
            return {'status': 1, 'data': 0}
        return {'status': 1, 'data': cursor}
    except Exception as e:
        return {'status': -1, 'data': 'document_exists ' + str(e)}

def insert_sentence(group_no, sentence, category):
    """ Insert the sentence in the collection.
    Args:
        group_no (int): the group to which the sentence belongs
        sentence (str): the sentence that is to be inserted
        category (str): the the category to which the sentence belongs

    Returns:
        (dict): the status which is 1, if successful and -1, if unsuccessful,
        and the data to be sent back, in this case, 1, or
        the description of the error.
    """

    try:
        #insert the sentence
        database.Sentences.insert_one({'group_no': group_no, 'sentence': sentence, 'category': category})
        return {'status': 1, 'data': 1}
    except Exception as e:
        return {'status': -1, 'data': 'insert_sentence ' + str(e)}



def insert_word_props(word, properties):
    """ Insert the word and its properties in the collection.

    Args:
        word (str): the word whose properties are to be stored
        properties (dict): the properies such as senses, length, consonant
        conjuncts, and frequency

    Returns:
        (dict): the status which is 1, if successful and -1, if unsuccessful,
        and the data, to be sent back, in this case, the description of the
        status, or the error, if any.
    """

    try:
        database.Words.insert_one(properties)
        return {'status': 1, 'data': 'Success'}
    except Exception as e:
        return {'status': -1, 'data': 'insert_word_props ' + str(e)}

def get_sentences(group_no):
    """ Retrieve all the sentences allotted to the group.

    Keyword Argument:
        group_no (str): the group from which the sentences are to be retrieved.

    Returns:
        (list): a list of sentences
    """
    query = {'group_no': group_no}
    sentences = []
    rows = database.Sentences.find(query, {'sentence': 1})
    for row in rows:
        sentences.append(row['sentence'])
    return sentences

def store_sentence_state(pid, sentence_number, sentences_complete):
    """ Store the current state of the participant.

    Keyword Arguments:
        pid (str): the participant ID
        sentence_number: the index of the sentence that was last displayed to the participant
        sentences_complete: a flag, which, if 1, indicates that all the sentences
        have been displayed to the user, and if 0, indicates that more sentences are remaining.

    Returns:
        (dict): the status which is 1, if successful and -1, if unsuccessful and also returns the
        description of the error.
    """
    try:
        #search for an existing state for the pid
        query = {'pid': pid}
        cursor = database['SentenceState'].find_one(query)
        if cursor is None:
            database.SentenceState.insert_one({'pid': pid, 'sentence_number': sentence_number, 'sentences_complete': sentences_complete})
        else:
            database.SentenceState.update_one(query, {'$set': {'pid': pid, 'sentence_number': sentence_number, 'sentences_complete': sentences_complete}})
        return {'status': 1, 'data': None}
    except Exception as e:
        return {'status': -1, 'data': str(e)}

def store_word_state(pid, sentence_number, word_number):
    """ Store the current state of the participant.

    Keyword Arguments:
        pid (str): the participant ID
        sentence_number: the index of the sentence that was last displayed to the participant
        word_number: the index of the word that was last displayed to the participant

    Returns:
        (dict): the status which is 1, if successful and -1, if unsuccessful and also returns the
        description of the error.
    """
    try:
        #search for an existing state for the pid
        query = {'pid': pid}
        cursor = database['WordsState'].find_one(query)
        if cursor is None:
            database.WordsState.insert_one({'pid': pid, 'sentence_number': sentence_number, 'word_number': word_number})
        else:
            database.WordsState.update_one(query, {'$set': {'pid': pid, 'sentence_number': sentence_number, 'word_number': word_number}})
        return {'status': 1, 'data': None}
    except Exception as e:
        return {'status': -1, 'data': str(e)}

def sentence_state_exists(pid):
    """ Check if the participant has a state in the database.

    Keyword Arguments:
        pid (str): the participant ID

    Returns:
        (dict): the state 1 if it exists, and 0, otherwise. The key 'data' would
        consist of the state details if the state exists, and 0, otherwise. If
        an error occurs, state would store -1 and data would consist of the
        description of the error.
    """
    try:
        #search for an existing state for the pid
        query = {'pid': pid}
        cursor = database['SentenceState'].find_one(query)
        if cursor is None:
            return {'state': 0, 'data': 0}
        else:
            return {'state': 1, 'data': {'sentence_number': cursor['sentence_number'], 'sentences_complete': cursor['sentences_complete']}}
    except Exception as e:
        return {'state': -1, 'data': str(e)}

def words_state_exists(pid):
    import sys
    """ Check if the participant has a state in the database.

    Keyword Arguments:
        pid (str): the participant ID

    Returns:
        (dict): the state 1 if it exists, and 0, otherwise. The key 'data' would
        consist of the state details if the state exists, and None, otherwise. If
        an error occurs, state would store -1 and data would consist of the
        description of the error.
    """
    try:
        #search for an existing state for the pid
        query = {'pid': pid}
        cursor = database['WordsState'].find_one(query)
        if cursor is None:
            return {'state': 1, 'data': None}
        else:
            print(cursor, file=sys.stdout)
            return {'state': 1, 'data': cursor}
    except Exception as e:
        return {'state': -1, 'data': str(e)}

def store_words(pid, words, sentence_number):
    """ Store the words selected by the participant.

    Keyword Arguments:
        pid (str): the participant ID
        words (list): the words selected by the participant
        sentence_number: the index of the sentence that was last displayed to the participant

    Returns:
        (dict): the status which is 1, if successful and -1, if unsuccessful and also returns the
        description of the error.
    """
    try:
        database.ComplexWords.insert_one({'pid': pid, 'words': words, 'sentence_number': sentence_number})
        return {'status': 1, 'data': None}
    except Exception as e:
        return {'status': -1, 'data': str(e)}

def get_words(pid):
    """ Return the words selected by the user for all the sentences.
    Keyword Argument:
        pid (str): the participant ID
    Returns:
        (dict): consists of the status which is 1, if successful and if records exist,
        0 if successful and if no records exist, and -1, if unsuccessful.
        The key 'data' consists of None, if no records were found. If records exist,
        a dictionary consisting of the sentence number and the corresponding words would be
        stored in 'data'.
    """
    try:
        #search for an existing state for the pid
        query = {'pid': pid}
        temp = {}
        cursor = database['ComplexWords'].find(query)
        if cursor is None:
            return {'status': 0, 'data': None}
        else:
            for document in cursor:
                temp[document['sentence_number']] = document['words']
        return {'status': 1, 'data': temp}
    except Exception as e:
        return {'status': -1, 'data': str(e)}
