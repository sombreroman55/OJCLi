import argparse
import configparser
import datetime
import json
import os
import random
import sys
import unicodedata
import webbrowser

import requests
import requests.exceptions

LANGUAGE_GUESS = {
    '.c': 'ANSI C',
    '.c++': 'C++',
    '.cc': 'C++',
    '.cpp': 'C++',
    '.cxx': 'C++',
    '.java': 'Java',
    '.pas': 'Pascal',
    '.py': 'Python 3',
}

LANGUAGE_VALUES = {
    'ANSI C':1,
    'Java':2,
    'C++':3,
    'Pascal':4,
    'C++11':5,
    'Python 3':6,
}

LANGUAGE_STRINGS = {
    1:'ANSI C',
    2:'Java',
    3:'C++',
    4:'Pascal',
    5:'C++11',
    6:'Python 3'
}

LANGUAGE_COLORS = {
    1:'white',
    2:'magenta',
    3:'yellow',
    4:'green',
    5:'red',
    6:'blue',
}

VERDICT_STRINGS = {
    10:'Submission Error',
    15:'Can\'t Be Judged',
    20:'In Queue',
    30:'Compile Error',
    35:'Restricted Function',
    40:'Runtime Error',
    45:'Output Limit',
    50:'Time Limit',
    60:'Memory Limit',
    70:'Wrong Answer',
    80:'Presentation Error',
    90:'Accepted'
}

VERDICT_COLORS = {
    10:'white',
    15:'white',
    20:'white',
    30:'yellow',
    35:'white',
    40:'cyan',
    45:'white',
    50:'blue',
    60:'black',
    70:'red',
    80:'magenta',
    90:'green'
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

def pretty_print_verdict(vdata):
    global USER_ID

    print('\n')
    verdict_headers = ['PROBLEM', 'VERDICT', 'LANG', 'TIME', 'RANK', 'SUBMIT TIME']

    col_widths = [-1] * 6
    table_data = [None] * 6 
    table_dlen = [None] * 6 

    for i in range(6):
        table_data[i] = list()
        table_dlen[i] = list()

    plong = -1
    for row in range(len(vdata)):
        pid = vdata[row][1]
        ps = str(PROBLEM_DATA[pid][1]) + ' ' + str(PROBLEM_DATA[pid][2])
        if len(ps) > plong:
            plong = len(ps)
        table_dlen[0].append(len(ps))
        table_data[0].append(ps)
    col_widths[0] = plong

    vlong = -1
    for row in range(len(vdata)):
        ver = vdata[row][2]
        vs = VERDICT_STRINGS[ver]
        if len(vs) > vlong:
            vlong = len(vs)
        table_dlen[1].append(len(vs))
        table_data[1].append(add_fg_color(vs, VERDICT_COLORS[ver]))
    col_widths[1] = vlong

    llong = -1
    for row in range(len(vdata)):
        lan = vdata[row][5]
        ls = LANGUAGE_STRINGS[lan]
        if len(ls) > llong:
            llong = len(ls)
        table_dlen[2].append(len(ls))
        table_data[2].append(add_fg_color(ls, LANGUAGE_COLORS[lan]))
    col_widths[2] = llong

    for row in range(len(vdata)):
        rt = int(vdata[row][3])
        rt = '%1.3f' % (rt / 1000.0)
        table_dlen[3].append(len(rt))
        table_data[3].append(rt)
    col_widths[3] = 5

    rlong = -1
    for row in range(len(vdata)):
        rank = vdata[row][6]
        rs = str(rank) if rank > 0 else '-'
        if len(rs) > rlong:
            rlong = len(rs)
        table_dlen[4].append(len(rs))
        table_data[4].append(rs)
    col_widths[4] = rlong

    slong = -1
    for row in range(len(vdata)):
        time = vdata[row][4]
        ss = datetime.datetime.utcfromtimestamp(time).strftime('%Y-%m-%d %H:%M:%S')
        if len(ss) > slong:
            slong = len(ss)
        table_dlen[5].append(len(ss))
        table_data[5].append(ss)
    col_widths[5] = slong

    top_div = ""
    div = ""
    bottom_div = ""
    for i in range(len(col_widths)):
        col_widths[i] = max(col_widths[i], len(verdict_headers[i]))
    for w in col_widths:
        top_div += ('\u2566\u2550' + ('\u2550' * (w+1)))
        div += ('\u256C\u2550' + ('\u2550' * (w+1)))
        bottom_div += ('\u2569\u2550' + ('\u2550' * (w+1)))

    top_div = top_div.replace('\u2566', '\u2554', 1)
    top_div += '\u2557'

    div = div.replace('\u256C', '\u2560', 1)
    div += '\u2563'

    bottom_div = bottom_div.replace('\u2569', '\u255A', 1)
    bottom_div += '\u255D'
    print(top_div)

    line = ""
    for i in range(len(col_widths)):
        diff = col_widths[i] - len(verdict_headers[i])
        pad = diff // 2
        line += '\u2551 '
        if diff % 2 == 1:
            line += ' '
        line += (' ' * pad) + add_decoration(verdict_headers[i].upper(), 'bold') + (' ' * pad)
        line += ' '
    line += '\u2551'
    print(line)

    for row in range(len(vdata)):
        line = ''
        for i in range(len(table_data)):
            diff = col_widths[i] - table_dlen[i][row]
            pad = diff // 2
            line += '\u2551 '
            if diff % 2 == 1:
                line += ' '
            line += (' ' * pad) + table_data[i][row] + (' ' * pad)
            line += ' '
        line += '\u2551'
        print(div)
        print(line)

    print(bottom_div)
    print('\n')


def pretty_print_rank(rank_data):
    global USER_ID

    print('\n')
    keys_to_pop = ['old', 'activity']
    for k in keys_to_pop:
        for row in range(len(rank_data)):
            rank_data[row].pop(k, None)
    rank_keys = list(rank_data[0].keys())
    col_widths = get_longest_fields(rank_data)
    top_div = ""
    div = ""
    bottom_div = ""
    for i in range(len(col_widths)):
        col_widths[i] = max(col_widths[i], len(rank_keys[i]))
    for w in col_widths:
        top_div += ('\u2566\u2550' + ('\u2550' * (w+1)))
        div += ('\u256C\u2550' + ('\u2550' * (w+1)))
        bottom_div += ('\u2569\u2550' + ('\u2550' * (w+1)))

    top_div = top_div.replace('\u2566', '\u2554', 1)
    top_div += '\u2557'

    div = div.replace('\u256C', '\u2560', 1)
    div += '\u2563'

    bottom_div = bottom_div.replace('\u2569', '\u255A', 1)
    bottom_div += '\u255D'
    print(top_div)

    line = ""
    for i in range(len(col_widths)):
        diff = col_widths[i] - len(rank_keys[i])
        pad = diff // 2
        line += '\u2551 '
        if diff % 2 == 1:
            line += ' '
        line += (' ' * pad) + add_decoration(rank_keys[i].upper(), 'bold') + (' ' * pad)
        line += ' '
    line += '\u2551'
    print(line)

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
            line += '\u2551 '
            if diff % 2 == 1:
                line += ' '
            line += (' ' * pad) + kstr + (' ' * pad)
            line += ' '
        line += '\u2551'
        print(div)
        print(line)

    print(bottom_div)
    print('\n')

def pretty_print_progress(progress_data, volume):
    global PROBLEM_VOLUMES

    print('\n')
    title = '\u2554' + ('\u2550' * 54) + ' PROGRESS ' + ('\u2550' * 54) + '\u2557'
    print(title)
    if volume:
        p = (progress_data[volume] * 100) // PROBLEM_VOLUMES[volume]
        line = "\u2551 Volume %3d " % volume
        line += '\u2580' * p
        line += ' ' * (100-p)
        line += ' %3d%% \u2551' % p
        print(line)
    else:
        total_ac = 0
        total_p = 0
        white = True
        for v in progress_data:
            total_ac += progress_data[v]
            total_p += PROBLEM_VOLUMES[v]
            p = (progress_data[v] * 100) // PROBLEM_VOLUMES[v]
            line = "Volume %3d " % v
            line += '\u2580' * p
            line += ' ' * (100-p)
            line += ' %3d%%' % p
            if white:
                line = add_fg_color(line, 'white')
            else:
                line = add_fg_color(line, 'yellow')
            white = not white
            line = '\u2551 ' + line + ' \u2551'
            print(line)

        p = (total_ac * 100) // total_p
        line = "       ALL "
        line += '\u2580' * p
        line += ' ' * (100-p)
        line += ' %3d%%' % p
        line = '\u2551 ' + line + ' \u2551'
        print(line)
    bottom = '\u255A' + ('\u2550' * 118) + '\u255D'
    print(bottom)
    print('\n')

def pretty_print_stats(sub_data, lan_data):
    total_subs = 0
    data = sub_data if sub_data else lan_data
    for key in data:
        total_subs += data[key]

    if sub_data:
        print('\n')
        title = '\u2554' + ('\u2550' * 44) + ' VERDICT STATISTICS ' + ('\u2550' * 44) + '\u2557'
        print(title)
        sub_data = {k: v for k, v in sorted(sub_data.items(), key=lambda x: x[1], reverse=True)}
        ticks = [(sub_data[x] * 100) // total_subs for x in sub_data]
        i = 0
        for key in sub_data:
            line = '\u2551 '
            cline = '%18s ' % VERDICT_STRINGS[key]
            cline += ('\u2580' * ticks[i])
            line += add_fg_color(cline, VERDICT_COLORS[key])
            line += (' ' * (ticks[0] - ticks[i]))
            line += '%4d submissions [%2d%%] \u2551' % (sub_data[key], ticks[i])
            print(line)
            i += 1
        bottom = '\u255A' + ('\u2550' * 108) + '\u255D'
        print(bottom)
        print('\n')

    if lan_data:
        if not sub_data:
            print('\n')
        title = '\u2554' + ('\u2550' * 30) + ' LANGUAGE STATISTICS ' + ('\u2550' * 31) + '\u2557'
        print(title)
        lan_data = {k: v for k, v in sorted(lan_data.items(), key=lambda x: x[1], reverse=True)}
        ticks = [(lan_data[x] * 100) // total_subs for x in lan_data]
        i = 0
        for key in lan_data:
            line = '\u2551 '
            cline = '%8s ' % LANGUAGE_STRINGS[key]
            cline += ('\u2580' * ticks[i])
            line += add_fg_color(cline, LANGUAGE_COLORS[key])
            line += (' ' * (ticks[0] - ticks[i]))
            line += '%4d submissions [%2d%%] \u2551' % (lan_data[key], ticks[i])
            print(line)
            i += 1
        bottom = '\u255A' + ('\u2550' * 82) + '\u255D'
        print(bottom)
        print('\n')
# ------------------------------------------------------------------------



# ------------------------------------------------------------------------
# Submit Command
# ------------------------------------------------------------------------
def submit_a(args):
    global CFG
    problem, ext = os.path.splitext(os.path.basename(args.files[0]))
    language = LANGUAGE_GUESS.get(ext, None)

    if args.problem:
        problem = args.problem

    if args.language:
        language = args.language

    if language is None:
        print('''\
No language specified, and I failed to guess language from filename
extension "%s"''' % (ext,))
        sys.exit(1)

    langnum = LANGUAGE_VALUES[language]
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
    global USER_ID

    vdata = get_verdicts(problem=problem, limit=limit)
    if USER_ID in vdata:
        vdata = vdata[USER_ID]
    vdata = list(reversed(vdata['subs']))
    if limit:
        vdata = vdata[:limit]
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
    if not submissions and not languages:
        submissions = languages = True
    stats(submissions=submissions, languages=languages)

def stats(submissions=True, languages=True):
    vdata = get_verdicts(problem=None, limit=None)
    vdata = vdata['subs']
    sdata = ldata = None
    if submissions:
        sdata = dict()
        for i in range(len(vdata)):
            ver = vdata[i][2]
            if not ver in sdata:
                sdata[ver] = 0
            sdata[ver] += 1
    if languages:
        ldata = dict()
        for i in range(len(vdata)):
            lan = vdata[i][5]
            if not lan in ldata:
                ldata[lan] = 0
            ldata[lan] += 1
    pretty_print_stats(sdata, ldata)
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
    subparsers = parser.add_subparsers(dest="cmd", description="Recognized commands", required=True)

    # sumbit sub-comand options
    submit_parser = subparsers.add_parser("submit", help="Submit a solution")
    submit_parser.add_argument('-p', '--problem', type=int,
        help="Specify problem(overrides problem best guess)")
    submit_parser.add_argument('-l', '--language', 
        help="Specify programming language (overrides language best guess)")
    submit_parser.set_defaults(func=submit_a)

    # verdict sub-comand options
    verdict_parser = subparsers.add_parser("verdict", help="See verdict data")
    verdict_exclusive = verdict_parser.add_mutually_exclusive_group()
    verdict_parser.add_argument('-p', '--problem', type=int,
        help="Get verdicts for specific problem. Gets all verdicts if this option is omitted.")
    verdict_exclusive.add_argument('-l', '--limit', type=int,
        help="Limits number of returned verdicts. Default is 25 verdicts.")
    verdict_exclusive.add_argument('-a', '--all', action='store_true',
        help="Returns all verdicts or all verdicts for problem if specified.")
    verdict_parser.set_defaults(func=verdict_a)

    # rank sub-comand options
    rank_parser = subparsers.add_parser("rank", help="See world or problem-specific rank")
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
    random_parser = subparsers.add_parser("random", help="Get a random problem to solve")
    random_parser.add_argument('-v', '--volume', type=int,
        help="Restrict random choice to specific problem volume")
    random_parser.set_defaults(func=random_prb_a)

    # progress sub-comand options
    progress_parser = subparsers.add_parser("progress", help="Show problem set progress")
    progress_parser.add_argument('-v', '--volume', type=int,
        help="Restrict progress to specific problem volume")
    progress_parser.set_defaults(func=progress_a)

    # stats sub-comand options
    stats_parser = subparsers.add_parser("stats", help="Show statistics about submissions")
    stats_parser.add_argument('-s', '--submissions', action='store_true',
        help='Only show statistics on submissions')
    stats_parser.add_argument('-l', '--languages', action='store_true',
        help='Only show statistics on languages')
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
