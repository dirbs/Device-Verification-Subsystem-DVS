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

import json
import shutil
import copy
import pytest
import httpretty
from testing.postgresql import Postgresql

from os import path
import yaml
import configparser


# pylint: disable=redefined-outer-name
@pytest.yield_fixture(scope='session')
def app(tmpdir_factory):
    """Method to create an app for testing."""
    # need to import this late as it might have side effects
    from app import app as app_
    from app import celery

    # need to save old configurations of the app
    # to restore them later upon tear down
    old_url_map = copy.copy(app_.url_map)
    old_view_functions = copy.copy(app_.view_functions)
    app_.testing = True
    app_.debug = False
    old_config = copy.copy(app_.config)

    # set task always eager to true in celery configurations in order to run celery tasks synchronously
    app_.config['task_always_eager'] = True
    celery.conf.update(app_.config)

    # update configuration file path
    global_config = yaml.load(open(path.abspath(path.dirname(__file__) + "/unittest_data/config.yml")))
    app_.config['system_config'] = global_config

    # update conditions file path
    conditions = yaml.load(open(path.abspath(path.dirname(__file__)+"/unittest_data/conditions.yml")))
    app_.config['conditions'] = conditions

    config = configparser.ConfigParser()
    config.read(path.abspath(path.dirname(__file__)+"/unittest_data/config.ini"))
    app_.config['dev_config'] = config

    temp_tasks = tmpdir_factory.mktemp('tasks')
    temp_reports = tmpdir_factory.mktemp('reports')

    # update upload directories path
    app_.config['dev_config']['UPLOADS']['task_dir'] = str(temp_tasks) # path to task_ids file upload
    app_.config['dev_config']['UPLOADS']['report_dir'] = str(temp_reports)  # path to non compliant report upload

    # initialize temp database and yield app
    postgresql = Postgresql()
    app_.config['SQLALCHEMY_DATABASE_URI'] = postgresql.url()
    yield app_

    # restore old configs after successful session
    app_.url_map = old_url_map
    app_.view_functions = old_view_functions
    app_.config = old_config
    shutil.rmtree(path=str(temp_tasks))
    shutil.rmtree(path=str(temp_reports))
    postgresql.stop()


@pytest.fixture(scope='session')
def flask_app(db, app):
    """fixture for injecting flask test client into every test."""

    yield app.test_client()


@pytest.yield_fixture(scope='session')
def db(app):
    """fixture to inject temp db instance into tests."""
    # need to import this late it might cause problems
    from app import db

    # create and configure database
    db.app = app
    db.create_all()
    yield db

    # teardown database
    db.drop_all()


@pytest.yield_fixture(scope='session')
def session(db):
    """Fixture for injecting database connection session into the tests."""
    connection = db.engine.connect()
    transaction = connection.begin()

    options = dict(bind=connection, binds={})
    session_ = db.create_scoped_session(options=options)
    db.session = session_

    yield session_

    transaction.rollback()
    connection.close()
    session_.remove()


@pytest.fixture(scope='session')
def mocked_imei_data():
    """Fixture for mocking core IMEI responses for tests."""
    mocked_imei_path = path.abspath(path.dirname(__file__) + '/unittest_data/imei.json')
    with open(mocked_imei_path) as f:
        data = json.load(f)
        yield data


@pytest.fixture(scope='session')
def mocked_tac_data():
    """Fixture for mocking core tac responses for tests."""
    mocked_tac_path = path.abspath(path.dirname(__file__) + '/unittest_data/tac.json')
    with open(mocked_tac_path) as f:
        data = json.load(f)
        yield data


@pytest.fixture(scope='session')
def mocked_reg_data():
    """Fixture for mocking core registration responses for tests."""
    mocked_tac_path = path.abspath(path.dirname(__file__) + '/unittest_data/registration.json')
    with open(mocked_tac_path) as f:
        data = json.load(f)
        yield data


@pytest.fixture(scope='session')
def mocked_subscribers_data():
    """Fixture for mocking core subscribers responses for tests."""
    mocked_tac_path = path.abspath(path.dirname(__file__) + '/unittest_data/subscribers.json')
    with open(mocked_tac_path) as f:
        data = json.load(f)
        yield data


@pytest.fixture(scope='session')
def mocked_pairings_data():
    """Fixture for mocking core pairings responses for tests."""
    mocked_tac_path = path.abspath(path.dirname(__file__) + '/unittest_data/pairings.json')
    with open(mocked_tac_path) as f:
        data = json.load(f)
        yield data


@pytest.yield_fixture(scope='session')
def dirbs_core_mock(app, mocked_tac_data, mocked_imei_data, mocked_reg_data, mocked_subscribers_data, mocked_pairings_data):
    """Monkey patch DIRBS-Core calls made by DVS."""
    httpretty.enable()

    single_tac_response = mocked_tac_data['single_tac_resp']
    gsma_not_found_imei_response = mocked_imei_data['gsma_not_found_imei']
    local_stolen_imei_response = mocked_imei_data['local_stolen_imei']
    not_registered_imei_response = mocked_imei_data['not_on_registration_list']
    duplicate_imei_response = mocked_imei_data['duplicate_imei']
    non_compliant_imei_response = mocked_imei_data['non_compliant_imei']
    p_non_complaint_imei_response = mocked_imei_data['provisionally_non_compliant']
    p_complaint_imei_response = mocked_imei_data['provisionally_compliant']
    complaint_imei_response = mocked_imei_data['compliant']
    reg_response = mocked_reg_data['registration_info']
    subscribers_resp = mocked_subscribers_data
    pairings_resp = mocked_pairings_data
    imei_batch_resp = mocked_imei_data['bulk']

    # mock dirbs core url
    dirbs_core_api = app.config['dev_config']['dirbs_core']['BaseUrl']
    dirbs_core_api_version = app.config['dev_config']['dirbs_core']['Version']

    # mock dirbs core registration data call for IMEI: 89764532901234
    httpretty.register_uri(httpretty.GET,
                           '{0}/{1}/imei/89764532901234/info'.format(dirbs_core_api, dirbs_core_api_version),
                           body=json.dumps({}), content_type='application/json', status=502)

    # mock dirbs core subscribers data call for IMEI: 89764532901234
    httpretty.register_uri(httpretty.GET, '{0}/{1}/imei/89764532901234/subscribers'.format(dirbs_core_api,
                                                                                           dirbs_core_api_version),
                           data=dict(limit=10, offset=1),
                           body=json.dumps(subscribers_resp), content_type='application/json', status=200)

    # mock dirbs core pairings data call for IMEI: 89764532901234
    httpretty.register_uri(httpretty.GET,
                           '{0}/{1}/imei/89764532901234/pairings'.format(dirbs_core_api, dirbs_core_api_version),
                           data=dict(limit=10, offset=1),
                           body=json.dumps(pairings_resp), content_type='application/json', status=200)

    # mock dirbs core registration data call for IMEI: 87654321901234
    httpretty.register_uri(httpretty.GET,
                           '{0}/{1}/imei/87654321901234/info'.format(dirbs_core_api, dirbs_core_api_version),
                           body=json.dumps({}), content_type='application/json', status=200)

    # mock dirbs core subscribers data call for IMEI: 87654321901234
    httpretty.register_uri(httpretty.GET, '{0}/{1}/imei/87654321901234/subscribers'.format(dirbs_core_api,
                                                                                           dirbs_core_api_version),
                           data=dict(limit=10, offset=1),
                           body=json.dumps(subscribers_resp), content_type='application/json', status=200)

    # mock dirbs core pairings data call for IMEI: 87654321901234
    httpretty.register_uri(httpretty.GET,
                           '{0}/{1}/imei/87654321901234/pairings'.format(dirbs_core_api, dirbs_core_api_version),
                           data=dict(limit=10, offset=1),
                           body=json.dumps(pairings_resp), content_type='application/json', status=200)

    # mock dirbs core registration data call for IMEI: 12345678904321
    httpretty.register_uri(httpretty.GET,
                           '{0}/{1}/imei/12345678904321/info'.format(dirbs_core_api, dirbs_core_api_version),
                           body=json.dumps({}), content_type='application/json', status=200)

    # mock dirbs core subscribers data call for IMEI: 12345678904321
    httpretty.register_uri(httpretty.GET, '{0}/{1}/imei/12345678904321/subscribers'.format(dirbs_core_api,
                                                                                           dirbs_core_api_version),
                           data=dict(limit=10, offset=1),
                           body=json.dumps(subscribers_resp), content_type='application/json', status=200)

    # mock dirbs core pairings data call for IMEI: 12345678904321
    httpretty.register_uri(httpretty.GET,
                           '{0}/{1}/imei/12345678904321/pairings'.format(dirbs_core_api, dirbs_core_api_version),
                           data=dict(limit=10, offset=1),
                           body=json.dumps(pairings_resp), content_type='application/json', status=200)

    # mock dirbs core registration data call for IMEI: 87654321904321
    httpretty.register_uri(httpretty.GET,
                           '{0}/{1}/imei/87654321904321/info'.format(dirbs_core_api, dirbs_core_api_version),
                           body=json.dumps(reg_response), content_type='application/json', status=200)

    # mock dirbs core subscribers data call for IMEI: 87654321904321
    httpretty.register_uri(httpretty.GET, '{0}/{1}/imei/87654321904321/subscribers'.format(dirbs_core_api,
                                                                                           dirbs_core_api_version),
                           data=dict(limit=10, offset=1),
                           body=json.dumps(subscribers_resp), content_type='application/json', status=200)

    # mock dirbs core pairings data call for IMEI: 87654321904321
    httpretty.register_uri(httpretty.GET,
                           '{0}/{1}/imei/87654321904321/pairings'.format(dirbs_core_api, dirbs_core_api_version),
                           data=dict(limit=10, offset=1),
                           body=json.dumps(pairings_resp), content_type='application/json', status=200)

    # mock dirbs core registration data call for IMEI: 12345678901234
    httpretty.register_uri(httpretty.GET, '{0}/{1}/imei/12345678901234/info'.format(dirbs_core_api, dirbs_core_api_version),
                           body=json.dumps(reg_response), content_type='application/json', status=200)

    # mock dirbs core subscribers data call for IMEI: 12345678901234
    httpretty.register_uri(httpretty.GET, '{0}/{1}/imei/12345678901234/subscribers'.format(dirbs_core_api,
                                                                                        dirbs_core_api_version),
                           data=dict(limit=10, offset=1),
                           body=json.dumps(subscribers_resp), content_type='application/json', status=200)

    # mock dirbs core pairings data call for IMEI: 12345678901234
    httpretty.register_uri(httpretty.GET,
                           '{0}/{1}/imei/12345678901234/pairings'.format(dirbs_core_api, dirbs_core_api_version),
                           data=dict(limit=10, offset=1),
                           body=json.dumps(pairings_resp), content_type='application/json', status=200)

    # mock dirbs core registration data call for IMEI: 12345678901111
    httpretty.register_uri(httpretty.GET,
                           '{0}/{1}/imei/12345678901111/info'.format(dirbs_core_api, dirbs_core_api_version),
                           body=json.dumps(reg_response), content_type='application/json', status=200)

    # mock dirbs core subscribers data call for IMEI: 12345678901111
    httpretty.register_uri(httpretty.GET, '{0}/{1}/imei/12345678901111/subscribers'.format(dirbs_core_api,
                                                                                           dirbs_core_api_version),
                           data=dict(limit=10, offset=1),
                           body=json.dumps(subscribers_resp), content_type='application/json', status=200)

    # mock dirbs core pairings data call for IMEI: 12345678901111
    httpretty.register_uri(httpretty.GET,
                           '{0}/{1}/imei/12345678901111/pairings'.format(dirbs_core_api, dirbs_core_api_version),
                           data=dict(limit=10, offset=1),
                           body=json.dumps(pairings_resp), content_type='application/json', status=200)

    # mock dirbs core registration data call for IMEI: 12345678902222
    httpretty.register_uri(httpretty.GET,
                           '{0}/{1}/imei/12345678902222/info'.format(dirbs_core_api, dirbs_core_api_version),
                           body=json.dumps(reg_response), content_type='application/json', status=200)

    # mock dirbs core subscribers data call for IMEI: 12345678902222
    httpretty.register_uri(httpretty.GET, '{0}/{1}/imei/12345678902222/subscribers'.format(dirbs_core_api,
                                                                                           dirbs_core_api_version),
                           data=dict(limit=10, offset=1),
                           body=json.dumps(subscribers_resp), content_type='application/json', status=200)

    # mock dirbs core pairings data call for IMEI: 12345678902222
    httpretty.register_uri(httpretty.GET,
                           '{0}/{1}/imei/12345678902222/pairings'.format(dirbs_core_api, dirbs_core_api_version),
                           data=dict(limit=10, offset=1),
                           body=json.dumps(pairings_resp), content_type='application/json', status=200)

    # mock dirbs core registration data call for IMEI: 12345678903333
    httpretty.register_uri(httpretty.GET,
                           '{0}/{1}/imei/12345678903333/info'.format(dirbs_core_api, dirbs_core_api_version),
                           body=json.dumps(reg_response), content_type='application/json', status=200)

    # mock dirbs core subscribers data call for IMEI: 12345678903333
    httpretty.register_uri(httpretty.GET, '{0}/{1}/imei/12345678903333/subscribers'.format(dirbs_core_api,
                                                                                           dirbs_core_api_version),
                           data=dict(limit=10, offset=1),
                           body=json.dumps(subscribers_resp), content_type='application/json', status=200)

    # mock dirbs core pairings data call for IMEI: 12345678903333
    httpretty.register_uri(httpretty.GET,
                           '{0}/{1}/imei/12345678903333/pairings'.format(dirbs_core_api, dirbs_core_api_version),
                           data=dict(limit=10, offset=1),
                           body=json.dumps(pairings_resp), content_type='application/json', status=200)

    # mock tac call for tac: 12345678
    httpretty.register_uri(httpretty.GET, '{0}/{1}/tac/12345678'.format(dirbs_core_api, dirbs_core_api_version),
                           body=json.dumps(single_tac_response), content_type='application/json')

    # mock tac call for tac: 87654321
    httpretty.register_uri(httpretty.GET, '{0}/{1}/tac/87654321'.format(dirbs_core_api, dirbs_core_api_version),
                           body=json.dumps({'gsma': None, 'tac': 87654321}), content_type='application/json')

    # mock tac call for tac: 89764532
    httpretty.register_uri(httpretty.GET, '{0}/{1}/tac/89764532'.format(dirbs_core_api, dirbs_core_api_version),
                           body=json.dumps(single_tac_response), content_type='application/json', status=502)

    # mock dirbs core imei call for IMEI: 12345678904321
    httpretty.register_uri(httpretty.GET,
                           '{0}/{1}/imei/12345678904321'.format(dirbs_core_api, dirbs_core_api_version),
                           body=json.dumps(complaint_imei_response), content_type='application/json', status=200)

    # mock dirbs core imei call for IMEI: 87654321904321
    httpretty.register_uri(httpretty.GET,
                           '{0}/{1}/imei/87654321904321'.format(dirbs_core_api, dirbs_core_api_version),
                           body=json.dumps(p_complaint_imei_response), content_type='application/json', status=200)

    # mock dirbs core imei call for IMEI: 87654321901234
    httpretty.register_uri(httpretty.GET,
                           '{0}/{1}/imei/87654321901234'.format(dirbs_core_api, dirbs_core_api_version),
                           body=json.dumps(p_non_complaint_imei_response), content_type='application/json', status=200)

    # mock dirbs core imei call for IMEI: 89764532901234
    httpretty.register_uri(httpretty.GET,
                           '{0}/{1}/imei/89764532901234'.format(dirbs_core_api, dirbs_core_api_version),
                           body=json.dumps(non_compliant_imei_response), content_type='application/json', status=200)

    # mock dirbs core imei call for IMEI: 12345678901111
    httpretty.register_uri(httpretty.GET, '{0}/{1}/imei/12345678901111'.format(dirbs_core_api, dirbs_core_api_version),
                           body=json.dumps(gsma_not_found_imei_response), content_type='application/json')

    # mock dirbs core imei call for IMEI: 12345678902222
    httpretty.register_uri(httpretty.GET, '{0}/{1}/imei/12345678902222'.format(dirbs_core_api, dirbs_core_api_version),
                           body=json.dumps(local_stolen_imei_response), content_type='application/json')

    # mock dirbs core imei call for IMEI: 12345678903333
    httpretty.register_uri(httpretty.GET, '{0}/{1}/imei/12345678903333'.format(dirbs_core_api, dirbs_core_api_version),
                           body=json.dumps(not_registered_imei_response), content_type='application/json')

    # mock dirbs core imei call for IMEI: 12345678904444
    httpretty.register_uri(httpretty.GET, '{0}/{1}/imei/12345678904444'.format(dirbs_core_api, dirbs_core_api_version),
                           body=json.dumps(duplicate_imei_response), content_type='application/json')

    # mock dirbs core imei call for IMEI: 12345678905555
    httpretty.register_uri(httpretty.GET, '{0}/{1}/imei/12345678905555'.format(dirbs_core_api, dirbs_core_api_version),
                           body=json.dumps(non_compliant_imei_response), content_type='application/json')

    # mock dirbs core imei call for IMEI: 12345678906666
    httpretty.register_uri(httpretty.GET, '{0}/{1}/imei/12345678906666'.format(dirbs_core_api, dirbs_core_api_version),
                           body=json.dumps(p_non_complaint_imei_response), content_type='application/json')

    # mock dirbs core imei call for IMEI: 12345678907777
    httpretty.register_uri(httpretty.GET, '{0}/{1}/imei/12345678907777'.format(dirbs_core_api, dirbs_core_api_version),
                           body=json.dumps(p_complaint_imei_response), content_type='application/json')

    # mock dirbs core imei call for IMEI: 12345678908888
    httpretty.register_uri(httpretty.GET, '{0}/{1}/imei/12345678908888'.format(dirbs_core_api, dirbs_core_api_version),
                           body=json.dumps(complaint_imei_response), content_type='application/json')

    # mock dirbs core imei call for IMEI: 12345678909999
    httpretty.register_uri(httpretty.GET, r'{0}/{1}/imei/12345678909999'.format(dirbs_core_api, dirbs_core_api_version),
                           body=json.dumps({}), content_type='application/json', status=502)

    # mock dirbs core imei call for IMEI: 12345678901234
    httpretty.register_uri(httpretty.GET,
                           r'{0}/{1}/imei/12345678901234'.format(dirbs_core_api, dirbs_core_api_version),
                           body=json.dumps(non_compliant_imei_response), content_type='application/json', status=200)

    # mock dirbs core imei batch call
    httpretty.register_uri(httpretty.POST,
                           r'{0}/{1}/imei-batch'.format(dirbs_core_api, dirbs_core_api_version),
                           data={"imeis": ["01206400000001", "353322asddas00303", "12344321000020", "35499405000401",
                                           "35236005000001", "01368900000001"]},
                           body=json.dumps(imei_batch_resp), content_type='application/json', status=200)

    # mock dirbs core imei batch call
    httpretty.register_uri(httpretty.POST,
                           r'{0}/{1}/imei-batch'.format(dirbs_core_api, dirbs_core_api_version),
                           data={"imeis": ["12345678901234"]},
                           body=json.dumps({}), content_type='application/json', status=502)

    yield

    # disable afterwards when not in use to avoid issues with the sockets
    # reset states
    httpretty.disable()
    httpretty.reset()


@pytest.yield_fixture(scope='session')
def mocked_captcha_call(app):
    """Monkey patch Captcha call in case of success."""
    token = app.config['dev_config']['secret_keys']['web']
    
    httpretty.enable()

    # mock dirbs core imei apis
    httpretty.register_uri(httpretty.POST,
                           'https://www.google.com/recaptcha/api/siteverify', data=dict(response='12345token', secret=token),
                           body=json.dumps({"success": True}), content_type='application/json', status=200)

    yield

    # disable afterwards when not in use to avoid issues with the sockets
    # reset states
    httpretty.disable()
    httpretty.reset()


@pytest.yield_fixture(scope='session')
def mocked_captcha_failed_call(app):
    """Monkey patch Captcha call in case of failure."""
    token = app.config['dev_config']['secret_keys']['web']

    httpretty.enable()

    # mock dirbs core imei apis
    httpretty.register_uri(httpretty.POST,
                           'https://www.google.com/recaptcha/api/siteverify',
                           data=dict(response='tokenforfailedcaptcha', secret=token),
                           body=json.dumps({"success": None}), content_type='application/json', status=200)

    yield

    # disable afterwards when not in use to avoid issues with the sockets
    # reset states
    httpretty.disable()
    httpretty.reset()
