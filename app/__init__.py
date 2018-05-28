
import configparser
from flask import Flask

app = Flask(__name__)

try:
    config = configparser.ConfigParser()
    config.read("config.ini")

    Root = str(config['DIRBS']['DirbsCore'])  # core api url
    GlobalConfig = config['CONFIG']  # load global configs
    AllowedFiles = str(config['ALLOWED_FILES']['AllowedExt']) # allowed file type for bulk check
    UploadDir = str(config['UPLOAD']['UploadFolder']) # path to upload folder of non-compliance report
    BaseUrl = str(config['ROOT']['BaseUrl']) # app root url
    Host = str(config['SERVER']['Host']) # Server Host
    Port = int(config['SERVER']['Port']) # Server Port

    from app.api.v1 import *
    app.register_blueprint(public_api, url_prefix=BaseUrl)
    app.register_blueprint(admin_api, url_prefix=BaseUrl)
    app.register_blueprint(bulk_api, url_prefix=BaseUrl)

except Exception as e:
    print(e)
