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

def store_state(pid, sentence_number, sentences_complete):
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
        cursor = database['State'].find_one(query)
        if cursor is None:
            database.State.insert_one({'pid': pid, 'sentence_number': sentence_number, 'sentences_complete': sentences_complete})
        else:
            database.State.update_one(query, {'$set': {'pid': pid, 'sentence_number': sentence_number, 'sentences_complete': sentences_complete}})
        return {'status': 1, 'data': None}
    except Exception as e:
        return {'status': -1, 'data': str(e)}
