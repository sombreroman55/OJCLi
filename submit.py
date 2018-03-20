import requests
import re

def submit(session, pid, lang, src):
    LANGUAGES = {
            'c':        1,
            'java':     2,
            'c++':      3,
            'pascal':   4,
            'c++11':    5,
            'python':   6,
    }
    SUBMIT_URL = "http://uva.onlinejudge.org/index.php?option=com_onlinejudge&Itemid=25&page=save_submission"
    payload = {
            'problemid':    '',
            'category':     '',
            'localid':      pid,
            'language':     LANGUAGES[lang],
            'code':         src
    }
    session.post(url,data=payload)
