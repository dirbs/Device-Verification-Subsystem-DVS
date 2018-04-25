import unittest
from app import app


class BasicTestCase(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    def test_index_route(self):
        response = self.client.get('/', content_type='html/text')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b'Welcome to DVS')

    def test_base_route(self):
        response = self.client.get('/api/v1/base', content_type='html/text')
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.data, b'inside /api/v1/base')
