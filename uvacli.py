import requests
from lxml import html

LOGIN_URL = 'https://uva.onlinejudge.org'
#SUBMIT_URL = ""

# Login to UVa Online Judge website
def login(payload):
    pass

# Submit problem
def submit():
    pass

# Main method
def main():
    # Gather necessary payload data
    sesh = requests.session()
    login = sesh.get(LOGIN_URL)
    login_html = html.fromstring(login.text)
#    print(login_html)
    hiddens = login_html.xpath(r'//form//input[@type="hidden"]')
    payload = {x.attrib["name"]:x.attrib["value"] for x in hiddens}
    print(payload)

    # Create payload

    # Use payload to login

    # Navigate to submission page

    # Submit file to online judge

    # Receive verdict

if __name__ == "__main__":
    main()
