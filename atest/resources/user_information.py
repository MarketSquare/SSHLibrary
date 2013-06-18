HOST = "localhost"
USERNAME = "test"
PASSWORD = "test"
PROMPT = "$"

from os import environ
USERHOME = environ['HOME'].replace(environ['USER'], USERNAME)
