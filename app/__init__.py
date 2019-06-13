"""
 SPDX-License-Identifier: BSD-4-Clause-Clear

 Copyright (c) 2018-2019 Qualcomm Technologies, Inc.

 All rights reserved.

 Redistribution and use in source and binary forms, with or without modification, are permitted (subject to the
 limitations in the disclaimer below) provided that the following conditions are met:

 * Redistributions of source code must retain the above copyright notice, this list of conditions and the following
   disclaimer.
 * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following
   disclaimer in the documentation and/or other materials provided with the distribution.
 * All advertising materials mentioning features or use of this software, or any deployment of this software, or
   documentation accompanying any distribution of this software, must display the trademark/logo as per the details
   provided here: https://www.qualcomm.com/documents/dirbs-logo-and-brand-guidelines
 * Neither the name of Qualcomm Technologies, Inc. nor the names of its contributors may be used to endorse or promote
   products derived from this software without specific prior written permission.

 SPDX-License-Identifier: ZLIB-ACKNOWLEDGEMENT

 Copyright (c) 2018-2019 Qualcomm Technologies, Inc.

 This software is provided 'as-is', without any express or implied warranty. In no event will the authors be held liable
 for any damages arising from the use of this software.

 Permission is granted to anyone to use this software for any purpose, including commercial applications, and to alter
 it and redistribute it freely, subject to the following restrictions:

 * The origin of this software must not be misrepresented; you must not claim that you wrote the original software. If
   you use this software in a product, an acknowledgment is required by displaying the trademark/logo as per the details
   provided here: https://www.qualcomm.com/documents/dirbs-logo-and-brand-guidelines
 * Altered source versions must be plainly marked as such, and must not be misrepresented as being the original software.
 * This notice may not be removed or altered from any source distribution.

 NO EXPRESS OR IMPLIED LICENSES TO ANY PARTY'S PATENT RIGHTS ARE GRANTED BY THIS LICENSE. THIS SOFTWARE IS PROVIDED BY
 THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
 THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
 COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
 DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
 BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 POSSIBILITY OF SUCH DAMAGE.                                                               #
"""

import sys

import configparser
import yaml

from urllib3.util.retry import Retry
import requests
from requests.adapters import HTTPAdapter

from flask import Flask, request
from flask_cors import CORS
from flask_babel import Babel

from celery import Celery
from celery.schedules import crontab

from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
CORS(app)

try:
    global_config = yaml.safe_load(open("etc/config.yml"))
    app.config['system_config'] = global_config

    conditions = yaml.safe_load(open("etc/conditions.yml"))
    app.config['conditions'] = conditions

    config = configparser.ConfigParser()
    config.read("config.ini")
    app.config['dev_config'] = config

    CeleryConf = app.config['system_config']['celery']

    # requests session
    session = requests.Session()
    session.keep_alive = False
    retry = Retry(total=app.config['system_config']['global'].get('Retry'),
                  backoff_factor=0.01, status_forcelist=[502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    db_params = {
        'Host': app.config['dev_config']['Database']['Host'],
        'Port': app.config['dev_config']['Database']['Port'],
        'Database': app.config['dev_config']['Database']['Database'],
        'User': app.config['dev_config']['Database']['UserName'],
        'Password': app.config['dev_config']['Database']['Password']
    }

    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://%s:%s@%s:%s/%s' % \
                                            (db_params['User'], db_params['Password'], db_params['Host'],
                                             db_params['Port'], db_params['Database'])

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    app.config['SQLALCHEMY_POOL_SIZE'] = int(app.config['dev_config']['Database']['pool_size'])
    app.config['SQLALCHEMY_POOL_RECYCLE'] = int(app.config['dev_config']['Database']['pool_recycle'])
    app.config['SQLALCHEMY_MAX_OVERFLOW'] = int(app.config['dev_config']['Database']['overflow_size'])
    app.config['SQLALCHEMY_POOL_TIMEOUT'] = int(app.config['dev_config']['Database']['pool_timeout'])

    db = SQLAlchemy()
    db.init_app(app)

    # celery configurations
    app.config['CELERY_BROKER_URL'] = CeleryConf['RabbitmqUrl']
    app.config['result_backend'] = 'db+'+app.config['SQLALCHEMY_DATABASE_URI']  # CeleryConf['RabbitmqBackend']
    app.config['broker_pool_limit'] = None

    # register tasks
    app.config['imports'] = CeleryConf['CeleryTasks']

    # initialize celery
    celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])

    # schedule task
    celery.conf.beat_schedule = {
        'delete-every-hour': {
            'task': 'app.api.v1.helpers.tasks.CeleryTasks.delete_files',
            'schedule': crontab(minute=0, hour='*/1')
        },
    }

    # update configurations
    celery.conf.update(app.config)
    TaskBase = celery.Task


    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)


    celery.Task = ContextTask

    app.config['BABEL_DEFAULT_LOCALE'] = global_config['language_support']['default']
    app.config['LANGUAGES'] = global_config['language_support']['languages']
    babel = Babel(app)


    @babel.localeselector
    def get_locale():
        return request.accept_languages.best_match(app.config['LANGUAGES'])

    # application blueprints registration
    from app.api.v1 import *

except Exception as e:
    app.logger.info("Error occurred while parsing configurations.")
    app.logger.exception(e)
    sys.exit(1)
