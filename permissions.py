import datetime

from helpers import createArtifact, sign_permission_artefact

# Variables for TEST CASE generation
FLIGHT_PURPOSE = "Provisional test"
PAYLOAD_WEIGHT = "Not specified"
PAYLOAD_DETAILS = "Not specified"
START_TIME = datetime.datetime.now()
END_TIME = START_TIME + datetime.timedelta(minutes=60)
INCORRECT_COORDS = [[77, 12], [77, 13], [78, 13], [78, 12]]
drone_pub_key_fake = open("dgca_private.pem").read()

def generate_all_test_permission_artefacts(drone , drone_pub_key):
    # generate all the test case permission files with expected results for each
    test_cases = []
    perm = generate_bad_geo_artefact(drone , drone_pub_key)
    test_cases.append({'permission': perm , 'expected_result': False})
    perm = generate_bad_pin_artefact(drone , drone_pub_key)
    test_cases.append({'permission': perm , 'expected_result': False})
    perm = generate_bad_time_artefact(drone , drone_pub_key)
    test_cases.append({'permission': perm , 'expected_result': False})
    perm = generate_bad_sign_artefact(drone ,drone_pub_key)
    test_cases.append({'permission': perm , 'expected_result': False})
    perm = generate_valid_permission(drone , drone_pub_key)
    test_cases.append ({'permission': perm , 'expected_result': True})
    return test_cases


def generate_valid_permission(drone , drone_pub_key):
    coords = [[77.609316, 12.934158], [77.609852, 12.934796], [77.610646, 12.934183], [77.610100, 12.933551],[77.609316 ,12.934158] ]                        #placeholder , replace the coordinates with the correct one
    permission = createArtifact(drone, FLIGHT_PURPOSE, PAYLOAD_WEIGHT, PAYLOAD_DETAILS, START_TIME, END_TIME, coords, drone_pub_key)
    signed_permission = sign_permission_artefact(permission)
    return signed_permission


def generate_bad_sign_artefact(drone , drone_pub_key):
    coords = [[77.609316, 12.934158], [77.609852, 12.934796], [77.610646, 12.934183], [77.610100, 12.933551],[77.609316 ,12.934158]]                           #placeholder , replace the coordinates with the correct one
    permission = createArtifact(drone, FLIGHT_PURPOSE, PAYLOAD_WEIGHT, PAYLOAD_DETAILS, START_TIME, END_TIME, coords, drone_pub_key)
    # Signing the permission artefact with a a
    signed_permission = sign_permission_artefact(permission , private_key= "dgca_private_fake.pem")
    return signed_permission


def generate_bad_geo_artefact(drone , drone_pub_key):
    bad_coords = [[77.592402, 12.951447], [77.602959, 12.950946], [77.604418, 12.935554], [77.587767, 12.936809],[77.592402, 12.951447]]
    # coords = [[77, 12], [77, 13], [78, 13], [78, 12]]
    permission = createArtifact(drone, FLIGHT_PURPOSE, PAYLOAD_WEIGHT, PAYLOAD_DETAILS, START_TIME, END_TIME, bad_coords, drone_pub_key)
    signed_permission = sign_permission_artefact(permission)
    return signed_permission


def generate_bad_time_artefact(drone , drone_pub_key):
    # BAD time is currently the same as the start time.RPAS should not pass this
    coords = [[77.609316, 12.934158], [77.609852, 12.934796], [77.610646, 12.934183], [77.610100, 12.933551],[77.609316 ,12.934158]]                           #placeholder , replace the coordinates with the correct one
    permission = createArtifact(drone, FLIGHT_PURPOSE, PAYLOAD_WEIGHT, PAYLOAD_DETAILS, START_TIME, START_TIME, coords, drone_pub_key)
    signed_permission = sign_permission_artefact(permission)
    return signed_permission


def generate_bad_pin_artefact(drone , drone_pub_key):
    # Incorrect PIN is a invalid 6 digit PIN
    coords = [[77.609316, 12.934158], [77.609852, 12.934796], [77.610646, 12.934183], [77.610100, 12.933551],[77.609316 ,12.934158]]                           #placeholder , replace the coordinates with the correct one
    permission = createArtifact(drone, FLIGHT_PURPOSE, PAYLOAD_WEIGHT, PAYLOAD_DETAILS, START_TIME, END_TIME, coords, drone_pub_key, secret_pin=b'654321')
    signed_permission = sign_permission_artefact(permission)
    return signed_permission
