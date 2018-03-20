import requests
from bs4 import BeautifulSoup
from sys import stderr

# Checks if user is logged in
def logged_in_successfully(session):
    result = session.get('https://uva.onlinejudge.org/index.php?option=com_onlinejudge&Itemid=9')
    return result.text.find('You need to login') == -1

# Tries to log in using username and password and returns the logged in session
def login(username,password):
    sesh = requests.Session()
    payload = {}
    lpage = sesh.get('https://uva.onlinejudge.org/')
    loginsoup = BeautifulSoup(lpage.text, 'lxml')    

    # Get hidden fields for POST request
    try:
        hiddens = loginsoup.find('form', attrs={'id':'mod_loginform'}).find_all('input')
    except Exception:
        print "Failed to receive server response."
        return None
    for hid in hiddens:
        if hid.has_attr('value'):
            payload[hid['name'].encode('ascii','ignore')] = hid['value'].encode('ascii','ignore')

    # Put user data into payload
    payload['username'] = username
    payload['passwd'] = password
    payload['remember'] = 'yes'

    # Try to login
    LOGIN_URL = 'https://uva.onlinejudge.org/index.php?option=com_comprofiler&task=login'
    result = sesh.post(LOGIN_URL, data=payload)
    return sesh
