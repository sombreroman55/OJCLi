import argparse
import configparser
import json
import os
import random
import re
import sys
import webbrowser
from pprint import pprint

import requests
import requests.exceptions

_DEBUG = True
_LANGUAGE_GUESS = {
    '.c': 'ANSI C',
    '.c++': 'C++',
    '.cc': 'C++',
    '.cpp': 'C++',
    '.cxx': 'C++',
    '.h': 'C++',
    '.java': 'Java',
    '.pas': 'Pascal',
    '.py': 'Python 3',
}

PROBLEM_VOLUMES = {
      1:100,   2:100,   3:100,   4:100,   5:100,
      6:100,   7:100,   8:100,   9:100,  10:100, 
     11:100,  12:100,  13:100,  14:100,  15:100,
     16:100,  17: 61,
        
    100:100, 101:100, 102:100, 103:100, 104:100,
    105:100, 106:100, 107:100, 108:100, 109:100,
    110:100, 111:100, 112:100, 113:100, 114:100,
    115:100, 116:100, 117:100, 118:100, 119:100,
    120:100, 121:100, 122:100, 123:100, 124:100,
    125:100, 126:100, 127:100, 128:100, 129:100,
    130:100, 131:100, 132:100, 133:  4,
}

USER_ID = None
BASE_URL = 'https://uhunt.onlinejudge.org/api'
_HEADERS = {'User-Agent': 'oj-cli-submit'}

# hostname: onlinejudge.org
# submissionurl: https://onlinejudge.org/index.php?option=com_onlinejudge&Itemid=25
# submissionsurl: https://onlinejudge.org/index.php?option=com_onlinejudge&Itemid=9

# Config functions
class ConfigError(Exception):
    pass

def get_config():
    cfg = configparser.ConfigParser()
    if not cfg.read([os.path.join(os.getenv('HOME'), '.ojrc'),
                     os.path.join(os.path.dirname(sys.argv[0]), '.ojrc')]):
        raise ConfigError('''\
                Failed to read config file from the home directory 
                or from the same directory as this script. Please 
                ensure you have created one.''')
    return cfg

def login(login_url, username, password):
    login_args = {'user': username, 
                  'script': 'true',
                  'password': password}

    return requests.post(login_url, data=login_args, headers=_HEADERS)

def login_from_config(cfg):
    username = cfg.get('user', 'username')
    loginurl = 'https://onlinejudge.org/'
    password = None
    try:
        password = cfg.get('user', 'password')
    except configparser.NoOptionError:
        raise ConfigError('''
                No password found in config file!''')

    return login(loginurl, username, password)

def get_userid(name):
    name_api = f'/uname2uid/{name}'
    full_url = BASE_URL + name_api
    response = requests.get(full_url)
    return str(response.json())

# Pretty printers
def pretty_print_table(json_content):
    print(json_content)
    pass

def pretty_print_progress(json_content):
    print(json_content)
    pass

# Command handlers
def submit_a(args):
    problem = args.problem if args.problem else None
    language = args.language if args.language else None
    submit(problem=problem, language=language)

def submit(src_file=None, problem=None, language=None):
    print("Submit command!")

def verdict_a(args):
    problem = args.problem if args.problem else None
    if args.all:
        limit = None
    else:
        limit = args.limit if args.limit else 25
    verdict(problem=problem, limit=limit)

def verdict(problem=None, limit=None):
    global USER_ID
    if not problem:
        if not limit:
            verdict_api = f'/subs-user/{USER_ID}'
        else:
            verdict_api = f'/subs-user-last/{USER_ID}/{limit}'
    else:
        verdict_api = f'/subs-nums/{USER_ID}/{problem}/0'

    full_api = BASE_URL + verdict_api
    response = requests.get(full_api)
    pretty_print_table(response.json())
    return response.json()

def rank_a(args):
    if args.surround and (args.above or args.below):
        print('-C/--surround cannot be used with -a/--above or -b/--below!')
        sys.exit(1)
    if args.surround:
        above = args.surround
        below = args.surround
    else:
        above = args.above if args.above else 0
        below = args.below if args.below else 0
    rank(above=above, below=below)

def rank(above=0, below=0):
    global USER_ID

    rank_api = f'/ranklist/{USER_ID}/{above}/{below}'
    full_url = BASE_URL + rank_api
    response = requests.get(full_url)
    pretty_print_table(response.json())

def random_prb_a(args):
    volume = args.volume if args.volume else None
    random_prb(volume=volume)

def random_prb(volume=None):
    global PROBLEM_VOLUMES

    if not volume:
        volume = random.choice(list(PROBLEM_VOLUMES.keys()))
    if volume not in PROBLEM_VOLUMES.keys():
        print("Invalid volume selection!")
        sys.exit(1)

    problem_num = random.randint(0, PROBLEM_VOLUMES[volume]-1)
    problem_vol_num = volume * 100 + problem_num

    problem_api = f'/p/num/{problem_vol_num}'
    full_api = BASE_URL + problem_api
    
    response = requests.get(full_api)
    response_json = response.json()
    num = response_json['num']
    title = response_json['title']

    print(f'Selected problem {num} - {title}')
    print('Open in browser (y/N)?')
    if sys.stdin.readline().upper()[:-1] == 'Y':
        problem_url = f'https://onlinejudge.org/external/{volume}/{problem_vol_num}.pdf'
        webbrowser.open(problem_url)

def progress_a(args):
    volume = args.volume if args.volume else None
    progress(volume=volume)

def progress(volume=None):
    global PROBLEM_VOLUMES

    data = verdict(problem=None, limit=None)

    print("Progress command!")

def stats_a(args):
    submissions = args.submissions if args.submissions else False
    languages = args.languages if args.languages else False
    problems = args.problems if args.problems else False
    if not submissions and not languages and not problems:
        submissions = languages = problems = True
    stats(submissions=submissions, languages=languages, problems=problems)

def stats(submissions=True, languages=True, problems=True):
    print("Stats command!")

# Main method
def main():
    global USER_ID

    parser = argparse.ArgumentParser(description='Perform Online Judge actions from the command line')
    subparsers = parser.add_subparsers(dest="cmd", help="Recognized commands", required=True)

    # sumbit sub-comand options
    submit_parser = subparsers.add_parser("submit")
    submit_parser.add_argument('-p', '--problem', type=int,
        help="Specify problem(overrides problem best guess)")
    submit_parser.add_argument('-l', '--language', 
        help="Specify programming language (overrides language best guess)")
    submit_parser.set_defaults(func=submit_a)

    # verdict sub-comand options
    verdict_parser = subparsers.add_parser("verdict")
    verdict_exclusive = verdict_parser.add_mutually_exclusive_group()
    verdict_parser.add_argument('-p', '--problem', type=int,
        help="Get verdicts for specific problem. Gets all verdicts if this option is omitted.")
    verdict_exclusive.add_argument('-l', '--limit', type=int,
        help="Limits number of returned verdicts. Default is 25 verdicts.")
    verdict_exclusive.add_argument('-a', '--all', action='store_true',
        help="Returns all verdicts or all verdicts for problem if specified.")
    verdict_parser.set_defaults(func=verdict_a)

    # rank sub-comand options
    rank_parser = subparsers.add_parser("rank")
    rank_parser.add_argument('-p', '--problem', type=int,
        help="Get rank on a specific problem. Gets global user rank if this option is omitted.")
    rank_parser.add_argument('-a', '--above', type=int,
        help="Return usernames and ranks of N users above your rank.")
    rank_parser.add_argument('-b', '--below', type=int,
        help="Return usernames and ranks of N users below your rank.")
    rank_parser.add_argument('-C', '--surround', type=int,
        help="Return usernames and ranks of N users above and below your rank.")
    rank_parser.set_defaults(func=rank_a)

    # random sub-comand options
    random_parser = subparsers.add_parser("random")
    random_parser.add_argument('-v', '--volume', type=int,
        help="Restrict random choice to specific problem volume")
    random_parser.set_defaults(func=random_prb_a)

    # progress sub-comand options
    progress_parser = subparsers.add_parser("progress")
    progress_parser.add_argument('-v', '--volume', type=int,
        help="Restrict progress to specific problem volume")
    progress_parser.set_defaults(func=progress_a)

    # stats sub-comand options
    stats_parser = subparsers.add_parser("stats")
    stats_parser.add_argument('-s', '--submissions', action='store_true',
        help='Only show statistics on submissions')
    stats_parser.add_argument('-l', '--languages', action='store_true',
        help='Only show statistics on languages')
    stats_parser.add_argument('-p', '--problems', action='store_true',
        help='Only show statistics on solved problems')
    stats_parser.set_defaults(func=stats_a)

    args = parser.parse_args()

    try:
        cfg = get_config()
    except ConfigError as exc:
        print(exc)
        sys.exit(1)

    USER_ID = get_userid(cfg.get('user', 'username'))

    args.func(args)

if __name__ == "__main__":
    main()
