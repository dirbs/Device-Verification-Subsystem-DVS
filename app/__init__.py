import sys
import yaml
import configparser
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

try:
    global_config = yaml.load(open("etc/config.yml"))

    config = configparser.ConfigParser()
    config.read("config.ini")

    Root = global_config['dirbs_core']['BaseUrl']  # core api url
    version = global_config['dirbs_core']['Version']  # core api version
    GlobalConfig = global_config['global']  # load global configs
    AllowedFiles = global_config['allowed_file_types']['AllowedExt']  # allowed file type for bulk check
    UploadDir = global_config['upload_dir']['UploadFolder']  # path to upload folder of non-compliance report
    BaseUrl = global_config['application_root']['RootUrl']  # app root url

    Host = str(config['SERVER']['Host'])  # Server Host
    Port = int(config['SERVER']['Port'])  # Server Port

    from app.api.v1 import *
    app.register_blueprint(public_api, url_prefix=BaseUrl)
    app.register_blueprint(admin_api, url_prefix=BaseUrl)
    app.register_blueprint(bulk_api, url_prefix=BaseUrl)

except Exception as e:
    app.logger.info("Error occurred while parsing configurations and blueprint registration.")
    app.logger.exception(e)
    sys.exit(1)
