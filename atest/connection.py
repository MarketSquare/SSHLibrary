import os

basedir = os.path.dirname(__file__)

HOST = "localhost" #"172.21.106.53"
USERNAME = "test" #user"
PASSWORD = "test"
PROMPT = "$"

PUBKEY_USERNAME = 'testkey'
PUBKEY_PASSWORD = 'testkey'
PUBKEY_FILE = os.path.join(basedir, 'id_rsa')
INVALID_PUBKEY_USERNAME = 'invalid_key_username'
INVALID_PUBKEY_FILE = os.path.join(basedir, 'invalid_rsa')
