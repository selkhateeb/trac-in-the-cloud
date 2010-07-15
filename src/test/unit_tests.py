import logging
import unittest

class SuccessFailError(unittest.TestCase):

    def setUp(self):
        logging.info('In setUp()')
        
    def tearDown(self):
        logging.info('In tearDown()')

    def test_success(self):
        logging.info('Running test_success()')
        self.assertTrue(True)

    # This test causes an intentional failure.
    def test_failure(self):
        logging.info('Running test_failure()')
        self.assertTrue(False)

    # This test causes an intentional error.
    def test_error(self):
        logging.info('Running test_error()')
        raise Exception('expected exception')
