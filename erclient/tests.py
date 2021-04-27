import unittest, os
from erclient.list import communication_types_list

class TestStringMethods(unittest.TestCase):

    def test_er_client_id_exists(self):
        er_client_id = os.environ.get('ER_CLIENT_ID')
        self.assertIsNotNone(er_client_id, "ER_CLIENT_ID Environment var is missing")

    def test_er_client_secret_exists(self):
        er_client_secret = os.environ.get('ER_CLIENT_SECRET')
        self.assertIsNotNone(er_client_secret, "ER_CLIENT_SECRET Environment var is missing")

    def test_er_token_url_exists(self):
        er_client_secret = os.environ.get('ER_TOKEN_URL')
        self.assertIsNotNone(er_client_secret, "ER_TOKEN_URL Environment var is missing")

    def test_er_base_url_exists(self):
        er_client_secret = os.environ.get('ER_BASE_URL')
        self.assertIsNotNone(er_client_secret, "ER_BASE_URL Environment var is missing")

    def test_connects_to_er_and_returns_data(self):
        self.assertIsInstance(communication_types_list(), list)



if __name__ == '__main__':
    unittest.main()


