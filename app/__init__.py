import sys

import yaml
import configparser

from urllib3.util.retry import Retry
import requests
from requests.adapters import HTTPAdapter

from flask import Flask
from flask_cors import CORS

from celery import Celery
from celery.schedules import crontab

app = Flask(__name__)
CORS(app)

try:
    global_config = yaml.load(open("etc/config.yml"))

    conditions = yaml.load(open("etc/conditions.yml"))

    config = configparser.ConfigParser()
    config.read("config.ini")

    # importing configurable variables

    Root = global_config['dirbs_core']['BaseUrl']  # core api url
    version = global_config['dirbs_core']['Version']  # core api version
    GlobalConfig = global_config['global']  # load global configs
    AllowedFiles = global_config['allowed_file_types']['AllowedExt']  # allowed file type for bulk check
    UploadDir = global_config['upload_dir']  # path to upload folder of non-compliance report
    BaseUrl = global_config['application_root']['RootUrl']  # app root url
    ServerAddress = global_config['application_root']['ServerIP']  # server address
    CeleryConf = global_config['celery']

    Host = str(config['SERVER']['Host'])  # Server Host
    Port = int(config['SERVER']['Port'])  # Server Port

    # requests session

    session = requests.Session()
    retry = Retry(total=3, backoff_factor=1, status_forcelist=[502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    # celery configurations
    app.config['CELERY_BROKER_URL'] = CeleryConf['RabbitmqUrl']
    app.config['result_backend'] = CeleryConf['RabbitmqBackend']
    app.config['broker_pool_limit'] = None

    app.config['imports'] = CeleryConf['CeleryTasks']

    celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])

    celery.conf.beat_schedule = {
        'delete-every-hour': {
            'task': 'app.api.v1.helpers.scheduled.delete_files',
            'schedule': crontab(minute=0, hour='*/1')
        },
    }

    celery.conf.update(app.config)

    # application blueprints registration
    from app.api.v1 import *
    app.register_blueprint(public_api, url_prefix=BaseUrl)
    app.register_blueprint(admin_api, url_prefix=BaseUrl)
    app.register_blueprint(bulk_api, url_prefix=BaseUrl)

except Exception as e:
    app.logger.info("Error occurred while parsing configurations and blueprint registration.")
    app.logger.exception(e)
    sys.exit(1)
