
import configparser
from flask import Flask

app = Flask(__name__)

try:
    config = configparser.ConfigParser()
    config.read("config.ini")

    CORE_URL = str(config['DIRBS']['dirbs_core'])  # core api url
    GLOBAL_CONF = config['CONFIG']  # load global configs
    ALLOWED_FILES = str(config['ALLOWED_FILES']['allowed_extensions']) # allowed file type for bulk check
    UPLOAD_FOLDER = str(config['UPLOAD']['upload_folder']) # path to upload folder of non-compliance report
    # APPLICATION_ROOT = str(config['APPLICATION_ROOT']) #app root url

    from app.api.v1 import *

except Exception as e:
    print(e)
