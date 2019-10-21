import datetime
import os
import pytz
import random
import uuid

timezone = pytz.timezone("Asia/Calcutta")

from helpers import createArtifact, sign_permission_artefact

# Variables for TEST CASE generation
FLIGHT_PURPOSE = "Provisional test"
PAYLOAD_WEIGHT = "Not specified"
PAYLOAD_DETAILS = "Not specified"
START_TIME = datetime.datetime.now(timezone)
END_TIME = START_TIME + datetime.timedelta(minutes=random.randint(50,90))

# use a private key as a fake public key
fake_dgca_pri_key = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Resources", "dgca_private_fake.pem")


def generate_all_test_permission_artefacts(drone_id, drone_pub_key, coords, bad_coords):
    # generate all the test case permission files with expected results for each
    test_cases = []
    perm = generate_bad_geo_artefact(drone_id, drone_pub_key, bad_coords)
    test_cases.append({'permission': perm, 'expected_result': False, 'test': 'bad_geo'})
    perm = generate_bad_time_artefact(drone_id, drone_pub_key, coords)
    test_cases.append({'permission': perm, 'expected_result': False, 'test': 'bad_time'})
    perm = generate_bad_sign_artefact(drone_id, drone_pub_key, coords)
    test_cases.append({'permission': perm, 'expected_result': False, 'test': 'bad_sign'})
    perm = generate_valid_permission(drone_id, drone_pub_key, coords)
    test_cases.append({'permission': perm, 'expected_result': True, 'test': 'valid_pa'})
    return test_cases


def generate_valid_permission(drone_id, drone_pub_key, coords):
    # A passable permission artefact for which the RPAS should ARM/TAKEOFF
    permission = createArtifact(drone_id, FLIGHT_PURPOSE, PAYLOAD_WEIGHT,
                                PAYLOAD_DETAILS, START_TIME, END_TIME, coords,
                                drone_pub_key)
    signed_permission = sign_permission_artefact(permission)
    return signed_permission


def generate_bad_sign_artefact(drone_id, drone_pub_key, coords):
    # Signing the permission artefact with a fake key.
    permission = createArtifact(drone_id, FLIGHT_PURPOSE, PAYLOAD_WEIGHT,
                                PAYLOAD_DETAILS, START_TIME, END_TIME, coords,
                                drone_pub_key)
    signed_permission = sign_permission_artefact(permission,
                                                 private_key=fake_dgca_pri_key)
    return signed_permission


def generate_bad_geo_artefact(drone_id, drone_pub_key, bad_coords):
    # generate a permission artefact with incorrect coords.
    permission = createArtifact(drone_id, FLIGHT_PURPOSE, PAYLOAD_WEIGHT,
                                PAYLOAD_DETAILS, START_TIME, END_TIME,
                                bad_coords, drone_pub_key)
    signed_permission = sign_permission_artefact(permission)
    return signed_permission


def generate_bad_time_artefact(drone_id, drone_pub_key, coords, ):
    # BAD time is currently the same as the start time.RPAS should not pass this
    permission = createArtifact(drone_id, FLIGHT_PURPOSE, PAYLOAD_WEIGHT,
                                PAYLOAD_DETAILS, START_TIME - datetime.timedelta(minutes=random.randint(1,60)),
                                START_TIME - datetime.timedelta(minutes=random.randint(1,60)),
                                coords, drone_pub_key)
    signed_permission = sign_permission_artefact(permission)
    return signed_permission

def generate_tampered_artefact(drone_id, drone_pub_key, coords, ):
    # Tampered permission artefact is different from the bad signature permission artefact. This has the contents
    # changed after signing, whereas the other has the PA signed by a illegitimate entity.

    permission = createArtifact(drone_id, FLIGHT_PURPOSE, PAYLOAD_WEIGHT,
                                PAYLOAD_DETAILS, START_TIME, END_TIME, coords,
                                drone_pub_key)
    signed_permission = sign_permission_artefact(permission)
    from lxml import etree
    pa_obj = etree.ElementTree(signed_permission)
    root_obj = pa_obj.getroot()
    root_obj.attrib['txnId'] = str(uuid.uuid1())
    return root_obj
