# OJCLi

A command line program that allows you to submit a solution to the (formerly UVa) Online Judge from the command line. 
Inspired by [Kattis' submission script](https://github.com/Kattis/kattis-cli), though this program allows for more actions than just submission of solutions.

# Login Information

The program looks for a file called `.ojrc` which is just a simple text file that should be stored either in the home directory or in the same directory as this program. 
Create this file in a text editor and put your Online Judge username and password each on their own line. Hopefully later I will think of a more secure way for you to 
store your login information (my understanding is that plaintext is bad).

# Dependencies

This program is written for Python 3, and will therefore probably not work with Python 2. It uses the `requests`, `BeautifulSoup`, and `lxml` python modules. 
If you have `pip`, installing `lxml` and `BeautifulSoup` is rather easy, however `requests` can be a bit trickier.

# Using the Client

### Submitting a solution

Run the command:
```bash
python3 ~/ojcli.py submit [language] [problem-id] <file>
```
Where `-s` stands for "submit". The arguments necessary for the program to submit your solution are the language of your solution, which must be one of the following: c, java, c++, pascal, c++11, python; the problem id of the problem you wish to submit; and finally the file itself.

### Seeing submissions

Run the command:
```bash
python3 ~/ojcli.py verdict [problem] [--limit #/--all]
```
Where `-v` stands for "verdicts". Optionally, you can append the `--limit #` option where # is the number of the most recent submissions you wish to see, or the `--all` option, which returns all of your submissions. Without the optional flags, the default number of recent submission is 25.

### Statistics
