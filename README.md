# OJCLi

A command line program that allows you to submit a solution to the (formerly UVa) Online Judge from
the command line. Inspired by [Kattis' submission script](https://github.com/Kattis/kattis-cli),
though this program allows for more actions than just submission of solutions by taking advantage of
Felix Halim's very useful [uHunt API](https://uhunt.onlinejudge.org/api).

# Login Information
The program looks for a file called `.ojrc` which is just a simple text file that should be stored
either in the home directory or in the same directory as this program. The file should look like
this:

```text
[user]
username = <your-username>
password = <your-password>
```

# Dependencies
This program is written for Python 3.5+, and will therefore not work with Python 2. It depends on
the `requests` module and the `BeautifulSoup` module.

# Using the Client
```
usage: ojcli.py [-h] {submit,verdict,rank,random,progress,stats} ...

Perform UVa Online Judge actions from the command line

optional arguments:
  -h, --help            show this help message and exit

subcommands:
  Recognized commands

  {submit,verdict,rank,random,progress,stats}
    submit              Submit a solution
    verdict             See verdict data
    rank                See world or problem-specific rank
    random              Get a random problem to solve
    progress            Show problem set progress
    stats               Show statistics about submissions
```

### submit
```
usage: ojcli.py submit [-h] [-p PROBLEM] [-l LANGUAGE] files [files ...]

positional arguments:
  files

optional arguments:
  -h, --help            show this help message and exit
  -p PROBLEM, --problem PROBLEM
                        Specify problem(overrides problem best guess)
  -l LANGUAGE, --language LANGUAGE
                        Specify programming language (overrides language best guess)

```

### verdict
```
usage: ojcli.py verdict [-h] [-p PROBLEM] [-l LIMIT | -a]

optional arguments:
  -h, --help            show this help message and exit
  -p PROBLEM, --problem PROBLEM
                        Get verdicts for specific problem. Gets all verdicts if this option is omitted.
  -l LIMIT, --limit LIMIT
                        Limits number of returned verdicts. Default is 25 verdicts.
  -a, --all             Returns all verdicts or all verdicts for problem if specified.
```

### rank
```
usage: ojcli.py rank [-h] [-a ABOVE] [-b BELOW] [-C SURROUND] [-n NEXT]

optional arguments:
  -h, --help            show this help message and exit
  -a ABOVE, --above ABOVE
                        Return usernames and ranks of N users above your rank.
  -b BELOW, --below BELOW
                        Return usernames and ranks of N users below your rank.
  -C SURROUND, --surround SURROUND
                        Return usernames and ranks of N users above and below your rank.
  -n NEXT, --next NEXT  Show how many more accepted problems needed to ascend N ranks.
```

### random
```
usage: ojcli.py random [-h] [-v VOLUME]

optional arguments:
  -h, --help            show this help message and exit
  -v VOLUME, --volume VOLUME
                        Restrict random choice to specific problem volume
```

### progress
```
usage: ojcli.py progress [-h] [-v VOLUME]

optional arguments:
  -h, --help            show this help message and exit
  -v VOLUME, --volume VOLUME
                        Restrict progress to specific problem volume
```

### stats
```
usage: ojcli.py stats [-h] [-s] [-l]

optional arguments:
  -h, --help         show this help message and exit
  -s, --submissions  Only show statistics on submissions
  -l, --languages    Only show statistics on languages
```
