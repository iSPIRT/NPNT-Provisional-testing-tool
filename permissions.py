import datetime
import os
import pytz

timezone = pytz.timezone("Asia/Calcutta")

from helpers import createArtifact, sign_permission_artefact

# Variables for TEST CASE generation
FLIGHT_PURPOSE = "Provisional test"
PAYLOAD_WEIGHT = "Not specified"
PAYLOAD_DETAILS = "Not specified"
START_TIME = datetime.datetime.now(timezone)
END_TIME = START_TIME + datetime.timedelta(minutes=60)
# INCORRECT_COORDS = [[77, 12], [77, 13], [78, 13], [78, 12]]
# use a private key as a fake public key
fake_dgca_pri_key = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Resources", "dgca_private_fake.pem")


def generate_all_test_permission_artefacts(drone_id, drone_pub_key, coords, bad_coords):
    # generate all the test case permission files with expected results for each
    test_cases = []
    perm = generate_bad_geo_artefact(drone_id, drone_pub_key, bad_coords)
    test_cases.append({'permission': perm, 'expected_result': False, 'test': 'bad_geo'})
    perm = generate_bad_pin_artefact(drone_id, drone_pub_key, coords)
    test_cases.append({'permission': perm, 'expected_result': False, 'test': 'bad_pin'})
    perm = generate_bad_time_artefact(drone_id, drone_pub_key, coords)
    test_cases.append({'permission': perm, 'expected_result': False, 'test': 'bad_time'})
    perm = generate_bad_sign_artefact(drone_id, drone_pub_key, coords)
    test_cases.append({'permission': perm, 'expected_result': False, 'test': 'bad_sign'})
    perm = generate_valid_permission(drone_id, drone_pub_key, coords)
    test_cases.append({'permission': perm, 'expected_result': True, 'test': 'valid_pa'})
    return test_cases


def generate_valid_permission(drone_id, drone_pub_key, coords):
    # coords = [[77.609316, 12.934158], [77.609852, 12.934796],
    #           [77.610646, 12.934183], [77.610100, 12.933551], [77.609316,
    #                                                            12.934158]]  # placeholder , replace the coordinates with the correct one
    permission = createArtifact(drone_id, FLIGHT_PURPOSE, PAYLOAD_WEIGHT,
                                PAYLOAD_DETAILS, START_TIME, END_TIME, coords,
                                drone_pub_key)
    signed_permission = sign_permission_artefact(permission)
    return signed_permission


def generate_bad_sign_artefact(drone_id, drone_pub_key, coords):
    # coords = [[77.609316, 12.934158], [77.609852, 12.934796],
    #           [77.610646, 12.934183], [77.610100, 12.933551], [77.609316,
    #                                                            12.934158]]  # placeholder , replace the coordinates with the correct one
    permission = createArtifact(drone_id, FLIGHT_PURPOSE, PAYLOAD_WEIGHT,
                                PAYLOAD_DETAILS, START_TIME, END_TIME, coords,
                                drone_pub_key)
    # Signing the permission artefact with a a
    signed_permission = sign_permission_artefact(permission,
                                                 private_key=fake_dgca_pri_key)
    return signed_permission


def generate_bad_geo_artefact(drone_id, drone_pub_key, bad_coords):
    # bad_coords = [[77.592402, 12.951447], [77.602959, 12.950946],
    #               [77.604418, 12.935554], [77.587767, 12.936809],
    #               [77.592402, 12.951447]]
    # coords = [[77, 12], [77, 13], [78, 13], [78, 12]]
    permission = createArtifact(drone_id, FLIGHT_PURPOSE, PAYLOAD_WEIGHT,
                                PAYLOAD_DETAILS, START_TIME, END_TIME,
                                bad_coords, drone_pub_key)
    signed_permission = sign_permission_artefact(permission)
    return signed_permission


def generate_bad_time_artefact(drone_id, drone_pub_key, coords, ):
    # BAD time is currently the same as the start time.RPAS should not pass this
    # coords = [[77.609316, 12.934158], [77.609852, 12.934796],
    #           [77.610646, 12.934183], [77.610100, 12.933551], [77.609316,
    #                                                            12.934158]]  # placeholder , replace the coordinates with the correct one
    permission = createArtifact(drone_id, FLIGHT_PURPOSE, PAYLOAD_WEIGHT,
                                PAYLOAD_DETAILS, START_TIME, START_TIME, coords,
                                drone_pub_key)
    signed_permission = sign_permission_artefact(permission)
    return signed_permission


def generate_bad_pin_artefact(drone_id, drone_pub_key, coords):
    # Incorrect PIN is a invalid 6 digit PIN
    # coords = [[77.609316, 12.934158], [77.609852, 12.934796],
    #           [77.610646, 12.934183], [77.610100, 12.933551], [77.609316,
    #                                                            12.934158]]  # placeholder , replace the coordinates with the correct one
    permission = createArtifact(drone_id, FLIGHT_PURPOSE, PAYLOAD_WEIGHT,
                                PAYLOAD_DETAILS, START_TIME, END_TIME, coords,
                                drone_pub_key, secret_pin=b'654321')
    signed_permission = sign_permission_artefact(permission)
    return signed_permission
