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
        response = self.client.get('/api/v1/bulk', data=dict(file=(io.BytesIO(b"234567890123456	345678901234567	12345	1234af789012345	357380062353789"), 'imeis.tsv'), indicator="True"))
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data), 0)

    def test_bulk_file_post_route(self):
        response = self.client.get('/api/v1/bulk', data=dict(file=(io.BytesIO(b"234567890123456	345678901234567	12345	1234af789012345	357380062353789"), 'imeis.tsv'), indicator="True"))
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data), 0)

    def test_bulk_file_type(self):
        response = self.client.get('/api/v1/bulk', data=dict(file=(io.BytesIO(b"234567890123456	345678901234567	12345	1234af789012345	357380062353789"),'imeis.csv'), indicator="True"))
        self.assertEqual(response.status_code, 400)
        self.assertGreater(len(response.data), 0)
