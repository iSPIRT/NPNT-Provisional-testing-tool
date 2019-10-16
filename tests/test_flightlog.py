import unittest

from helpers import *
from permissions import generate_bad_sign_artefact, generate_tampered_artefact


#todo see if this requires renaming
class TestFlightLog(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.base_path = os.path.dirname(os.path.realpath(__file__))
        cls.unsigned_flight_log = os.path.join(cls.base_path, "unsigned_Flight_Log.json")
        cls.signed_flight_log = os.path.join(cls.base_path, "unsigned_Flight_Log-signed.json")
        cls.sample_public_key = os.path.join(cls.base_path, "sample_key_public.pem")
        cls.sample_private_key = os.path.join(cls.base_path, "sample_key_private.pem")
        cls.signed_valid_pa = os.path.join(cls.base_path, "signed_pa_valid.xml")
        cls.mock_dgca_cert = os.path.join(os.path.dirname(cls.base_path), "Resources" , "dgca.cert")
        cls.bad_artefact_file = os.path.join(cls.base_path, "bad_pa.xml")

    def test_flight_log_signature(self):
        sign_log(self.unsigned_flight_log, self.sample_private_key)
        self.assertTrue(verify_flight_log_signature(self.signed_flight_log, self.sample_public_key ))

    def test_permission_signature(self):
        # Test that a valid Permssion artefact is signed with the correct key.
        self.assertTrue(verify_xml_signature(self.signed_valid_pa, self.mock_dgca_cert))

    def test_bad_signature_pa(self):
        # Generate a badly signed PA and verify that it fails signature check
        coords = [[77.609316, 12.934158], [77.609852, 12.934796],[77.610646, 12.934183], [77.610100, 12.933551], [77.609316,12.934158]]

        with open(self.sample_public_key) as f:
            pub_key = f.read()
        my_art = generate_bad_sign_artefact("Rand_DRONENUM", pub_key,coords)
        from lxml import etree
        etree.ElementTree(my_art).write(self.bad_artefact_file)
        self.assertFalse(verify_xml_signature(xml_file=self.bad_artefact_file, certificate_path=self.mock_dgca_cert))

        # Verify that a tampered artefact also fails checks
        malart = generate_tampered_artefact("Rand_UIN", pub_key, coords)
        etree.ElementTree(malart).write(self.bad_artefact_file)
        self.assertFalse(verify_xml_signature(self.bad_artefact_file, self.mock_dgca_cert))

    # Sample method to generate a keypair
    # def test_keygen(self):
    #     create_keys(self.base_path, "sample_key")

    def tearDown(self) -> None:
        files_to_clean = [self.signed_flight_log, self.bad_artefact_file]
        for file in files_to_clean:
            if os.path.exists(file):
                os.remove(file)
