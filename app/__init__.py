
import configparser
from flask import Flask

app = Flask(__name__)

try:
    app.config.from_object('server_config.DevelopmentConfig')  # app configs
    app.config.from_object('server_config.GlobalConfig')  # app global configs


    # config = configparser.ConfigParser()
    # config.read("config.ini")

    Root = app.config['DIRBSCORE']  # core api url
    GlobalConfig = {"MinImeiLength": app.config['MIN_IMEI_LENGTH'],
                    "MaxImeiLength": app.config['MAX_IMEI_LENGTH'],
                    "MinImeiRange": app.config['MIN_IMEI_RANGE'],
                    "MaxImeiRange": app.config['MAX_IMEI_RANGE'],
                    "HelpUrl": app.config['HELP_URL'],
                    "BlockDate": app.config['BLOCK_DATE'],
                    "MinFileContent": app.config['MIN_FILE_CONTENT'],
                    "MaxFileContent": app.config['MAX_FILE_CONTENT']}  # load global configs
    AllowedFiles = app.config['ALLOWED_EXT'] # allowed file type for bulk check
    UploadDir = app.config['UPLOAD_FOLDER'] # path to upload folder of non-compliance report
    BaseUrl = app.config['BASE_URL'] # app root url
    Host = app.config['HOST'] # Server Host
    Port = app.config['PORT'] # Server Port

    from app.api.v1 import *
    app.register_blueprint(public_api, url_prefix=BaseUrl)
    app.register_blueprint(admin_api, url_prefix=BaseUrl)
    app.register_blueprint(bulk_api, url_prefix=BaseUrl)

except Exception as e:
    print(e)
