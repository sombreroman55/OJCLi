import os
import sys
import requests
import argparse
from pprint import pprint
from login import login, logged_in_successfully
from submit import submit
from sessions import read_session, write_session

_DEBUG = True

# Main method
def main():
    # Get user information from .logininfo file
    f = open('.logininfo', 'r')
    lines = f.read().splitlines()
    username = lines[0]
    password = lines[1]

    # Login
    sesh = login(username,password)
    if logged_in_successfully(sesh):
        print "Logged in successfully"
        write_session(sesh)
    else:
        print "Log in failed."
        exit(1) 
    
    pick = read_session()
    if pick is not None:
        print("Session file exists and is valid.")
    exit(0)

if __name__ == "__main__":
    main()
