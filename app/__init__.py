#######################################################################################################################
#                                                                                                                     #
# Copyright (c) 2018 Qualcomm Technologies, Inc.                                                                      #
#                                                                                                                     #
# All rights reserved.                                                                                                #
#                                                                                                                     #
# Redistribution and use in source and binary forms, with or without modification, are permitted (subject to the      #
# limitations in the disclaimer below) provided that the following conditions are met:                                #
# * Redistributions of source code must retain the above copyright notice, this list of conditions and the following  #
#   disclaimer.                                                                                                       #
# * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the         #
#   following disclaimer in the documentation and/or other materials provided with the distribution.                  #
# * Neither the name of Qualcomm Technologies, Inc. nor the names of its contributors may be used to endorse or       #
#   promote products derived from this software without specific prior written permission.                            #
#                                                                                                                     #
# NO EXPRESS OR IMPLIED LICENSES TO ANY PARTY'S PATENT RIGHTS ARE GRANTED BY THIS LICENSE. THIS SOFTWARE IS PROVIDED  #
# BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED #
# TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT      #
# SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR   #
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES LOSS OF USE,      #
# DATA, OR PROFITS OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,      #
# STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,   #
# EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.                                                                  #
#                                                                                                                     #
#######################################################################################################################

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
    task_dir = str(config['UPLOADS']['task_dir'])  # path to task_ids file upload
    report_dir = str(config['UPLOADS']['report_dir'])  # path to non compliant report upload
    BaseUrl = global_config['application_root']['RootUrl']  # app root url
    ServerAddress = global_config['application_root']['ServerIP']  # server address
    CeleryConf = global_config['celery']
    secret = global_config['secret_keys']  # secret keys for recaptcha validation

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

    # register tasks
    app.config['imports'] = CeleryConf['CeleryTasks']

    # initialize celery
    celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])

    # schedule task
    celery.conf.beat_schedule = {
        'delete-every-hour': {
            'task': 'app.api.v1.helpers.scheduled.delete_files',
            'schedule': crontab(minute=0, hour='*/1')
        },
    }

    # update configurations
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
