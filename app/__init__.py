
import configparser
from flask import Flask

app = Flask(__name__)

config = configparser.ConfigParser()
config.read("config.ini")

from app.api.v1 import *
