# UVaCLi

A command line script that allows you to submit a solution to the UVa Online Judge from the command line. Inspired by [Kattis' submission script](https://github.com/Kattis/kattis-cli).

# Login Information

The script currently looks for a file called `.logininfo` which is just a simple text file that should be stored in the same directory as this script. Create this file in a text editor and put your UVa username and password each on their own line. Hopefully later I will think of a more secure way for you to store your login information (my understanding is that plaintext is bad).

# Dependencies

This script uses the `requests` and `lxml` python modules. If you have `pip`, installing `lxml` is rather easy, however `requests` can be a bit trickier.

# Using the Client

To run the client, assuming you are in the same directory as the script, type the command:
```bash
python uvacli.py <source>
```

If you were not in the same directory, replace the `uvacli.py` with `path/to/file/uvacli.py`.

Or you can do what I do which is to symbolically link to wherever the script is on your machine from your home directory. On mac or Linux it would look something like this:
```bash
ln -s ~/absolute/path/to/script/uvacli.py ~/uvacli.py
```
Now the command above just becomes
```bash
python ~/uvacli.py <source>
```
and you're good to go!

# More Options

The client will try to predict the language and problem number based on the file name of your source file. If it is not of the form `XXXXX.y` where `XXXXX` represents the 5-digit numerical problem ID (for example, 00100, 11677, 01132, etc.) and `.y` represents the file extension of the language you used (i.e. `.c`, `.java`, etc.), it will not predict correctly. In that case, or if you want to specify anyway, you can use the following flags while submitting:

| Flag  | Function                  | Usage                                       |
| ----- | ------------------------- | ------------------------------------------- |
| -h    | Shows help, lists options | `python uvacli.py -h`                       |
| -p    | Overrides problem guess   | `python uvacli.py -p <problem-id> <source>` |
| -m    | Overrides mainclass guess | `python uvacli.py -m <mainclass> <source>`  | 
| -l    | Overrides language guess  | `python uvacli.py -l <language> <source>`   |
| -f    | Forces submission         | `python uvacli.py -f <source>`              |
