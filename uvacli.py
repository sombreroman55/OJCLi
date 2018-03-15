import requests
from lxml import html

LOGIN_URL = 'https://uva.onlinejudge.org'
SUBMIT_URL = 'https://uva.onlinejudge.org/index.php?option=com_onlinejudge&Itemid=25'
_DEBUG = True
_LANGUAGE_GUESS = {
    '.c': 'C',
    '.cc': 'C++',
    '.cpp': 'C++',
    '.h': 'C++',
    '.java': 'Java',
    '.pas': 'Pascal',
    '.py': 'Python'
}
_MAINCLASS_GUESS = { 'Java', 'Python' }

# Main method
def main():
    # Gather necessary payload data
    sesh = requests.session()
    login = sesh.get(LOGIN_URL)
    login_html = html.fromstring(login.text)
    hiddens = login_html.xpath(r'//form//input[@type="hidden"]')

    # Create payload
    payload = {x.attrib["name"]:x.attrib["value"] for x in hiddens}
    f = open(".logininfo", 'r')
    lines = f.read().splitlines()
    payload["username"] = lines[0]
    payload["password"] = lines[1]
    if (_DEBUG == True):
        print(payload)

    # Use payload to login
    response = sesh.post(LOGIN_URL, data=payload)

    # Navigate to submission page
    submit = sesh.get(SUBMIT_URL)

    # Submit file to online judge
    

    # Receive verdict

if __name__ == "__main__":
    main()
