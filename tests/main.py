import unittest
from .apitests.basic import BasicTestCase


def api_test_suite():
    api_suite = unittest.TestSuite()
    api_suite.addTest(BasicTestCase('test_index_route'))
    return api_suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(api_test_suite())
