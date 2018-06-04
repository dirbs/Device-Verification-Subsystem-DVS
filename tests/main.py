import unittest
from .apitests.basic import BasicTestCase


def api_test_suite():
    api_suite = unittest.TestSuite()
    api_suite.addTest(BasicTestCase('test_index_route'))
    api_suite.addTest(BasicTestCase('test_public_route'))
    api_suite.addTest(BasicTestCase('test_admin_route'))
    api_suite.addTest(BasicTestCase('test_admin_post_route'))
    api_suite.addTest(BasicTestCase('test_tac_count'))
    api_suite.addTest(BasicTestCase('test_bulk_route'))
    api_suite.addTest(BasicTestCase('test_bulk_post_route'))
    api_suite.addTest(BasicTestCase('test_bulk_file_route'))
    api_suite.addTest(BasicTestCase('test_bulk_file_post_route'))
    api_suite.addTest(BasicTestCase('test_bulk_file_type'))

    return api_suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(api_test_suite())
