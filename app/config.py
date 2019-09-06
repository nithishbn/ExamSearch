import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'secretkey'
    QUESTIONS_FOLDER = os.path.abspath("static")
    # SERVER_NAME = 'nithishnarasimman.com'