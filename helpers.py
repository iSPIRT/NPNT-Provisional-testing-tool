import base64
import json
from xml.etree.ElementTree import Element, SubElement, ElementTree

import signxml as sx
from Cryptodome.Cipher import PKCS1_v1_5
from Cryptodome.Hash import SHA256
from Cryptodome.PublicKey import RSA
from Cryptodome.Signature import pkcs1_15


def createArtifact(drone_uin, purpose, payloadWeight, payloadDetails,
                   startTime, endTime, coords, drone_pub_key_obj, secret_pin = b'1234'):
    """
    Create  a permission artefact for the required details. The artifact xml
    will be generated and the XML root object is returned. Saving tto a file is
    left to the user.

    Notes -
    * Recurring Time permission artefacts are not handled as the spec needs to finalize on that
    * PIN in encrypted without salt. Needs improvement on a standardized method

    :param str drone_uin: UIN of the RPAS (Not checked in some cases)
    :param str purpose: Flight purpose text
    :param str payloadWeight: payload wt in agreed upon units.
    :param str payloadDetails: details of payload
    :param datetime.datetime startTime: start time for the permission request
    :param datetime.datetime endTime: END time for the permission request
    :param List coords: List of coords in Long, Lat
    :param drone_pub_key_obj: The public key file object of the RPAS for PIN
    :param secret_pin: the secret PIN for the PA. defaults unless specified.
    :return: The permission artefact XML root object. Ready to be signed or stored
    """
    pinhash = create_pin_hash(drone_pub_key_obj, secret_pin= secret_pin )
    uap = Element('UAPermission',
                  {'lastUpdated': '',
                   'ttl': '',
                   'txnId': '',
                   'permissionArtifactId': '',
                   'pilotPinHash': pinhash})
    permission = SubElement(uap, 'Permission')
    owner = SubElement(permission, 'Owner', {'operatorId': ''})
    pilot = SubElement(owner, 'Pilot', {'uaplNo': '', 'validTo': ''})
    flight_details = SubElement(permission, 'FlightDetails')
    uad = SubElement(flight_details, 'UADetails', {'uinNo': drone_uin})

    purpose = SubElement(flight_details, 'FlightPurpose',
                         {'shortDesc': purpose,
                          'frequency': ''})

    payload = SubElement(flight_details, 'PayloadDetails',
                         {'payloadWeight': payloadWeight,
                          'payloadDetails': payloadDetails})

    params = SubElement(flight_details,'FlightParameters',
                        {'flightStartTime': startTime.isoformat(),
                         'flightEndTime': endTime.isoformat(),
                         'frequenciesUsed': ''})

    coordinates = SubElement(params, 'Coordinates')
    for ordinate in coords:
        SubElement(coordinates, 'Coordinate',
                   {'latitude': str(ordinate[1]),
                    'longitude': str(ordinate[0])})
    return ElementTree(uap)


def create_pin_hash(pub_key_obj, secret_pin=b'1234'):
    """
    Create the hash of Pilot PIN. The PINis encrypted with the public key of the
    drone. Default uses PIN of 1234 unless explicitly changed
    :param pub_key_obj: the public key object of the RPAS for PIN encryption
    :param secret_pin: the top secret pin for NPNT in action
    :return: the encrypted hash of the PIN
    """
    hashpin = SHA256.new(secret_pin).digest()
    key = RSA.import_key(pub_key_obj)

    cipher = PKCS1_v1_5.new(key)
    ciphertext = cipher.encrypt(hashpin)
    ciphertext = base64.b64encode(ciphertext)
    return str(ciphertext)[2:-1]


def sign_permission_artefact(xml_root, private_key="Resources/dgca_private.pem", certificate="Resources/dgca.cert" ):
    """
    Sign the permission artefact xml with the private key stored .
    Optionally pass a different key path to sign with a different key
    :param xml_root: the xml root object to sign
    :param private_key: the path to the private key to perform signing
    :return: the signed XML root object. Note - this needs to be saved as a file
    """
    root = xml_root.getroot()

    cert = open(certificate).read()
    key = open(private_key,"rb").read()
    signed_root = sx.XMLSigner()
    ns = {}
    ns[None] = signed_root.namespaces['ds']
    signed_root.namespaces = ns
    signed_root = signed_root.sign(root, key=key, cert=cert)
    return signed_root


def verify_flight_log_authenticity(log_object, public_key_obj):
    """
    Verify the signature of the Flight log_object against a public key.
    :param log_object: The flight log file object for verification
    :param public_key_obj: The public key object to be verified against
    :return: bool: True or False on success of verification
    """
    json_data = json.loads(log_object)
    flight_data_for_verification = bytes(str(json_data['FlightLog']).encode())
    signature = base64.b64decode(json_data['Signature'])
    public_key_obj = RSA.import_key(public_key_obj)
    sig_data = SHA256.new(bytes(flight_data_for_verification))
    try:
        pkcs1_15.new(public_key_obj).verify(sig_data, signature)
        # The file signature is authentic
        return True
    except ValueError:
        # The file signature is not authentic.
        return False


def sign_log(log_path, private_key_path):
    """
    sample function to demonstrate how to sign a flight log.
    This complements the verify_flight_log_signature methood
    :param log_path: path to log file to be signed
    :param private_key_path: path to the private key to be used for signing.
    :return: sign the flight log and save it with 'signed' added to it's name
    """
    log_obj = open(log_path, "rb").read()
    jd = json.loads(log_obj)
    key_ob = open(private_key_path).read()
    rsa_key = RSA.import_key(key_ob)

    hashed_logdata = SHA256.new(bytes(str((jd['FlightLog'])).encode()))
    log_signature = pkcs1_15.new(rsa_key).sign(hashed_logdata)

    # the signature is encoded in base64 for transport
    enc = base64.b64encode(log_signature)
    # dealing with python's byte string expression
    jd['Signature'] = str(enc)[2:-1]
    save_path = log_path[:-5] + "signed.json"
    with open(save_path, 'w') as outfile:
       json.dump(jd, outfile, indent =4)

