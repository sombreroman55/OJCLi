import argparse
import configparser
import json
import os
import random
import sys
import unicodedata
import webbrowser

import requests
import requests.exceptions

_LANGUAGE_GUESS = {
    '.c': 'ANSI C',
    '.c++': 'C++',
    '.cc': 'C++',
    '.cpp': 'C++',
    '.cxx': 'C++',
    '.java': 'Java',
    '.pas': 'Pascal',
    '.py': 'Python 3',
}

_LANGUAGE_VALUES = {
    'ANSI C': 1,
    'Java': 2,
    'C++': 3,
    'Pascal': 4,
    'C++11': 5,
    'Python 3': 6,
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

PROBLEM_DATA = None
PNUM_TO_PID = None
PID_TO_PNUM = None

CFG = None
USER_ID = None
BASE_URL = 'https://uhunt.onlinejudge.org/api'
_HEADERS = {'User-Agent': 'oj-cli-submit'}

# Only supporting 8 color mode for now
ANSI_FG_COLORS = {
    'black': '\u001b[30m',
    'red': '\u001b[31m',
    'green': '\u001b[32m',
    'yellow': '\u001b[33m',
    'blue': '\u001b[34m',
    'magenta': '\u001b[35m',
    'cyan': '\u001b[36m',
    'white': '\u001b[37m',
}

ANSI_BG_COLORS = {
    'black': '\u001b[40m',
    'red': '\u001b[41m',
    'green': '\u001b[42m',
    'yellow': '\u001b[43m',
    'blue': '\u001b[44m',
    'magenta': '\u001b[45m',
    'cyan': '\u001b[46m',
    'white': '\u001b[47m',
}

ANSI_DECORATIONS = {
    'bold': '\u001b[1m',
    'underline': '\u001b[4m',
    'reverse': '\u001b[7m'
}

ANSI_RESET = '\u001b[0m'

# ------------------------------------------------------------------------
# Config functions
# ------------------------------------------------------------------------
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
# ------------------------------------------------------------------------



# ------------------------------------------------------------------------
# Various helper functions
# ------------------------------------------------------------------------
def get_longest_field(data, column):
    longest = -1
    for row in range(len(data)):
        if len(str(data[row][column])) > longest:
            longest = len(str(data[row][column]))
    return longest

def get_longest_fields(data):
    longests = list()
    for key in data[0].keys():
        longests.append(get_longest_field(data, key))
    return longests

def get_problem_data():
    problem_data_url = '/p'
    full_url = BASE_URL + problem_data_url
    response = requests.get(full_url)
    data = dict()
    for row in response.json():
        data[row[0]] = row
    return data

def create_problem_lookups():
    global PROBLEM_DATA
    global PNUM_TO_PID
    global PID_TO_PNUM 

    PNUM_TO_PID = dict()
    PID_TO_PNUM = dict()

    for p in PROBLEM_DATA:
        pid = PROBLEM_DATA[p][0]
        pnum = PROBLEM_DATA[p][1]
        PID_TO_PNUM[pid] = pnum
        PNUM_TO_PID[pnum] = pid

def get_verdicts():
    pass
# ------------------------------------------------------------------------



# ------------------------------------------------------------------------
# Coloring functions
# ------------------------------------------------------------------------
def add_fg_color(text, color):
    if color in ANSI_BG_COLORS:
        text = ANSI_FG_COLORS[color] + text
        if not ANSI_RESET in text:
            text += ANSI_RESET
    return text

def add_bg_color(text, color):
    if color in ANSI_BG_COLORS:
        text = ANSI_BG_COLORS[color] + text
        if not ANSI_RESET in text:
            text += ANSI_RESET
    return text

def add_decoration(text, decoration):
    if decoration in ANSI_DECORATIONS:
        text = ANSI_DECORATIONS[decoration] + text
        if not ANSI_RESET in text:
            text += ANSI_RESET
    return text
# ------------------------------------------------------------------------



# ------------------------------------------------------------------------
# Pretty printers
# ------------------------------------------------------------------------
def display_len(text):
    res = 0
    for char in text:
        res += 2 if unicodedata.east_asian_width(char) == 'W' else 1
    return res

def pretty_print_verdict(verdict_data):
    print(verdict_data)

def pretty_print_rank(rank_data):
    global USER_ID
    if not rank_data:
        print("No rank data provided.")
        return

    print('\n')
    keys_to_pop = ['old', 'activity']
    for k in keys_to_pop:
        for row in range(len(rank_data)):
            rank_data[row].pop(k, None)
    rank_keys = list(rank_data[0].keys())
    col_widths = get_longest_fields(rank_data)
    div = ""
    for i in range(len(col_widths)):
        col_widths[i] = max(col_widths[i], len(rank_keys[i]))
    for w in col_widths:
        div += ("+-" + ('-' * (w+1)))
    div += '+'
    print(div)
    line = ""
    for i in range(len(col_widths)):
        diff = col_widths[i] - len(rank_keys[i])
        pad = diff // 2
        line += '| '
        if diff % 2 == 1:
            line += ' '
        line += (' ' * pad) + rank_keys[i].upper() + (' ' * pad)
        line += ' '
    line += '|'
    print(line)
    print(div)
    for r in rank_data:
        line = ""
        user = r['userid'] == int(USER_ID)
        rkeys = list(r.keys())
        for i in range(len(col_widths)):
            if isinstance(r[rkeys[i]], int):
                klen = len(str(r[rkeys[i]]))
                kstr = str(r[rkeys[i]])
            elif isinstance(r[rkeys[i]], str):
                klen = display_len(r[rkeys[i]])
                kstr = str(r[rkeys[i]])

            if user:
                kstr = add_fg_color(kstr, 'yellow')
                kstr = add_decoration(kstr, 'bold')

            diff = col_widths[i] - klen
            pad = diff // 2
            line += '| '
            if diff % 2 == 1:
                line += ' '
            line += (' ' * pad) + kstr + (' ' * pad)
            line += ' '
        line += '|'
        print(line)
        print(div)
    print('\n')

def pretty_print_progress(progress_data, volume):
    global PROBLEM_VOLUMES

    print('\n')
    title = ('*' * 55) + ' PROGRESS ' + ('*' * 55)
    print(title)
    if volume:
        p = (progress_data[volume] * 100) // PROBLEM_VOLUMES[volume]
        line = "Volume %3d   [" % volume
        line += '=' * p
        line += ' ' * (100-p)
        line += '] %3d%%' % p
        print(line)
    else:
        total_ac = 0
        total_p = 0
        white = True
        for v in progress_data:
            total_ac += progress_data[v]
            total_p += PROBLEM_VOLUMES[v]
            p = (progress_data[v] * 100) // PROBLEM_VOLUMES[v]
            line = "Volume %3d   [" % v
            line += '=' * p
            line += ' ' * (100-p)
            line += '] %3d%%' % p
            if white:
                line = add_fg_color(line, 'white')
            else:
                line = add_fg_color(line, 'yellow')
            white = not white
            print(line)

        p = (total_ac * 100) // total_p
        line = "       ALL   ["
        line += '=' * p
        line += ' ' * (100-p)
        line += '] %3d%%' % p
        print(line)

    print('\n')

def pretty_print_stats(stats_data):
    pass
# ------------------------------------------------------------------------



# ------------------------------------------------------------------------
# Submit Command
# ------------------------------------------------------------------------
def submit_a(args):
    global CFG
    problem, ext = os.path.splitext(os.path.basename(args.files[0]))
    language = _LANGUAGE_GUESS.get(ext, None)

    if args.problem:
        problem = args.problem

    if args.language:
        language = args.language

    if language is None:
        print('''\
No language specified, and I failed to guess language from filename
extension "%s"''' % (ext,))
        sys.exit(1)

    langnum = _LANGUAGE_VALUES[language]
    files = list(set(args.files))

    try:
        login_reply = login_from_config(CFG)
    except ConfigError as exc:
        print(exc)
        sys.exit(1)
    except requests.exceptions.RequestException as err:
        print('Login connection failed:', err)
        sys.exit(1)

    if not login_reply.status_code == 200:
        print('Login failed.')
        if login_reply.status_code == 403:
            print('Incorrect username or password/token (403)')
        elif login_reply.status_code == 404:
            print('Incorrect login URL (404)')
        else:
            print('Status code:', login_reply.status_code)
        sys.exit(1)

    submit(login_reply.cookies, problem, langnum, files)

def submit(cookies, problem, language, files):
    submit_url = 'https://onlinejudge.org/index.php?option=com_onlinejudge&Itemid=25'
    data = {'submit': 'true',
            'language': language,
            'localid': problem,
            'script': 'true'}

    codeupl = []
    for f in files:
        with open(f) as code:
            codeupl.append(('codeupl',
                              (os.path.basename(f),
                               code.read(),
                               'application/octet-stream')))

    try:
        result = requests.post(submit_url, data=data, files=codeupl, cookies=cookies, headers=_HEADERS)
    except requests.exceptions.RequestException as err:
        print('Submit connection failed:', err)
        sys.exit(1)

    if result.status_code != 200:
        print('Submission failed.')
        if result.status_code == 403:
            print('Access denied (403)')
        elif result.status_code == 404:
            print('Incorrect submit URL (404)')
        else:
            print('Status code:', login_reply.status_code)
        sys.exit(1)

    plain_result = result.content.decode('utf-8').replace('<br />', '\n')
    print(plain_result)
# ------------------------------------------------------------------------



# ------------------------------------------------------------------------
# Verdict Command
# ------------------------------------------------------------------------
def verdict_a(args):
    problem = args.problem if args.problem else None
    if args.all:
        limit = None
    else:
        limit = args.limit if args.limit else 25
    verdict(problem=problem, limit=limit)

def get_verdicts(problem=None, limit=None):
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
    return response.json()

def verdict(problem=None, limit=None):
    vdata = get_verdicts(problem=problem, limit=limit)
    pretty_print_verdict(vdata)
# ------------------------------------------------------------------------



# ------------------------------------------------------------------------
# Rank Command
# ------------------------------------------------------------------------
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
    _next = args.next if args.next else 0
    rank(above=above, below=below, _next=_next)

def rank(above=0, below=0, _next=0):
    global USER_ID

    rank_api = f'/ranklist/{USER_ID}/{above}/{below}'
    full_url = BASE_URL + rank_api
    response = requests.get(full_url)
    rdata = response.json()

    if _next > 0:
        rank_api = f'/ranklist/{USER_ID}/{_next}/0'
        full_url = BASE_URL + rank_api
        response = requests.get(full_url)
        data = response.json()
        acs_needed = data[0]['ac'] - data[-1]['ac']
        desired_rank = data[0]['rank']
        line = 'Need ' 
        line += add_fg_color(f'{acs_needed}', 'green')
        line += f' more accepted solutions to reach rank {desired_rank}.\n'
        pretty_print_rank(rdata)
        print(line)
    else:
        pretty_print_rank(rdata)
# ------------------------------------------------------------------------



# ------------------------------------------------------------------------
# Random Command
# ------------------------------------------------------------------------
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
# ------------------------------------------------------------------------



# ------------------------------------------------------------------------
# Progress Command
# ------------------------------------------------------------------------
def progress_a(args):
    volume = args.volume if args.volume else None
    progress(volume=volume)

def progress(volume=None):
    global PROBLEM_VOLUMES
    global PID_TO_PNUM

    data = get_verdicts(problem=None, limit=None)
    data = data['subs']
    nums = set()
    for i in range(len(data)):
        if data[i][2] == 90:
            nums.add(PID_TO_PNUM[data[i][1]])
    pdata = dict()
    for k in PROBLEM_VOLUMES.keys():
        pdata[k] = 0

    for n in nums:
        idx = n // 100
        pdata[idx] += 1

    pretty_print_progress(pdata, volume)
# ------------------------------------------------------------------------



# ------------------------------------------------------------------------
# Stats Command
# ------------------------------------------------------------------------
def stats_a(args):
    submissions = args.submissions if args.submissions else False
    languages = args.languages if args.languages else False
    problems = args.problems if args.problems else False
    if not submissions and not languages and not problems:
        submissions = languages = problems = True
    stats(submissions=submissions, languages=languages, problems=problems)

def stats(submissions=True, languages=True, problems=True):
    print("Stats command!")
# ------------------------------------------------------------------------



# ------------------------------------------------------------------------
# Main method
# ------------------------------------------------------------------------
def main():
    global PROBLEM_DATA
    global USER_ID
    global CFG

    PROBLEM_DATA = get_problem_data()
    create_problem_lookups()

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
    rank_parser.add_argument('-n', '--next', type=int,
        help="Show how many more accepted problems needed to ascend N ranks.")
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
        CFG = get_config()
    except ConfigError as exc:
        print(exc)
        sys.exit(1)

    USER_ID = get_userid(CFG.get('user', 'username'))

    args.func(args)

if __name__ == "__main__":
    main()
