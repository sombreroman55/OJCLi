import os
import pickle
import requests
from hashlib import md5

LOCATION = os.getcwd()
SESSION_NAME = os.path.join(LOCATION, ".uvasession")
SESSION_CHECKSUM = os.path.join(LOCATION, ".uvachecksum") 

def exists_session():
    try:
        open(SESSION_NAME)
        open(SESSION_CHECKSUM)
    except Exception:
        return False
    return True

def valid_session():
    seshfile = open(SESSION_NAME).read();
    hashfile = open(SESSION_CHECKSUM).read();
    return md5(seshfile).hexdigest() == hashfile
    pass

def read_session():
    if not exists_session():
        return None
    elif not valid_session():
        return None
    return pickle.load(open(SESSION_NAME))

def write_session(session):
    try:
        pickle.dump(session, open(SESSION_NAME, 'w'))
        open(SESSION_CHECKSUM, 'w').write(md5(open(SESSION_NAME).read()).hexdigest())
    except:
        print "Failed to write session.\nDo you have permission to access \"{0}\" and \"{1}\"?".format(SESSION_NAME, SESSION_CHECKSUM)
        exit(1)
