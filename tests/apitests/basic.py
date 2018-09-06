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

import unittest
from app import app
import io


class BasicTestCase(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    def test_index_route(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b'{"message": "Welcome to DVS"}')

    def test_public_route(self):
        response = self.client.get('/api/v1/basicstatus?imei=357380062353789')
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data), 0)

    def test_admin_route(self):
        response = self.client.get('/api/v1/fullstatus?imei=357380062353789&seen_with=0&start=1&limit=3')
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data), 0)

    def test_admin_post_route(self):
        response = self.client.post('/api/v1/fullstatus?imei=357380062353789&seen_with=1&start=1&limit=3')
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data), 0)

    def test_tac_count(self):
        tac = "86034120"
        count = "000000"
        tac = int(tac+count)
        for x in range(1000000):
            tac1 = tac+x
        self.assertEqual(tac1, 86034120999999)

    def test_bulk_route(self):
        response = self.client.get('/api/v1/bulk', data=dict(tac='86453223', indicator='False'))
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data), 0)

    def test_bulk_post_route(self):
        response = self.client.post('/api/v1/bulk', data=dict(tac='86453223', indicator='False'))
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data), 0)

    def test_bulk_file_route(self):
        response = self.client.get('/api/v1/bulk', data=dict(file=(io.BytesIO(b"234567890123456	345678901234567	12345	"
                                                                              b"1234af789012345	357380062353789"),
                                                                   'imeis.tsv'), indicator="True"))
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data), 0)

    def test_bulk_file_post_route(self):
        response = self.client.get('/api/v1/bulk', data=dict(file=(io.BytesIO(b"234567890123456	345678901234567	12345	"
                                                                              b"1234af789012345	357380062353789"),
                                                                   'imeis.tsv'), indicator="True"))
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data), 0)

    def test_bulk_file_type(self):
        response = self.client.get('/api/v1/bulk', data=dict(file=(io.BytesIO(b"234567890123456	345678901234567	12345	"
                                                                              b"1234af789012345	357380062353789"),
                                                                   'imeis.csv'), indicator="True"))
        self.assertEqual(response.status_code, 400)
        self.assertGreater(len(response.data), 0)
