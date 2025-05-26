import unittest

from azure_function_doctor import utils


class TestUtils(unittest.TestCase):
    def test_python_version(self):
        self.assertTrue(utils.check_python_version())
