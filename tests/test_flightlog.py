import unittest
import os
from helpers import *


class TestFlightLog(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.base_path = os.path.dirname(os.path.realpath(__file__))
        cls.unsigned_flight_log = os.path.join(cls.base_path, "unsigned_Flight_Log.json")
        cls.signed_flight_log = os.path.join(cls.base_path, "unsigned_Flight_Log-signed.json")
        cls.sample_public_key = os.path.join(cls.base_path, "sample_key_public.pem")
        cls.sample_private_key = os.path.join(cls.base_path, "sample_key_private.pem")

    def test_flight_log_signature(self):
        sign_log(self.unsigned_flight_log, self.sample_private_key)
        self.assertTrue(verify_flight_log_signature(self.signed_flight_log, self.sample_public_key ))

    # Sample method to generate a keypair
    # def test_keygen(self):
    #     create_keys(self.base_path, "sample_key")

    def tearDown(self) -> None:
        if os.path.exists(self.signed_flight_log):
            os.remove(self.signed_flight_log)
