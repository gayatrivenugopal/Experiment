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
