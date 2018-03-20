# UVaCLi

A command line script that allows you to submit a solution to the UVa Online Judge from the command line. Inspired by [Kattis' submission script](https://github.com/Kattis/kattis-cli).

# Login Information

The script currently looks for a file called `.logininfo` which is just a simple text file that should be stored in the same directory as this script. Create this file in a text editor and put your UVa username and password each on their own line. Hopefully later I will think of a more secure way for you to store your login information (my understanding is that plaintext is bad).

# Dependencies

This script uses the `requests`, `BeautifulSoup`, and `lxml` python modules. If you have `pip`, installing `lxml` and `BeautifulSoup` is rather easy, however `requests` can be a bit trickier.

# Using the Client

After downloading the script whereever you wish, I recommend symlinking to the script from your home directory to allow you to easily access it. Run the following command in macOS/Linux to do so:

```bash
ln -s ~/absolute/path/to/script/uvacli.py ~/uvacli.py
```

To run the client, you must run the script with one of the following flags and arguments:

### Submitting a solution

Run the command:
```bash
python ~/uvacli.py -s <language> <problem-id> <file>
```
Where `-s` stands for "submit". The arguments necessary for the script to submit your solution are the language of your solution, which must be one of the following: c, java, c++, pascal, c++11, python; the problem id of the problem you wish to submit; and finally the file itself.

### Seeing submissions

Run the command:
```bash
python ~/uvacli.py -v [--limit #/--all]
```
Where `-v` stands for "verdicts". Optionally, you can append the `--limit #` option where # is the number of the most recent submissions you wish to see, or the `--all` option, which returns all of your submissions. Without the optional flags, the default number of recent submission is 25.

### Seeing submissions for a specific problem
Run the command:
```bash
python ~/uvacli.py -pv <problem-id>
```
Where `-pv` stands for "problem-id verdicts". This will return all submissions for the given problem ID.
