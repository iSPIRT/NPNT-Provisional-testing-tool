import base64
import json
import os
from xml.etree.ElementTree import Element, SubElement, ElementTree

import cryptography
import signxml as sx
from Cryptodome.Cipher import PKCS1_v1_5
from Cryptodome.Hash import SHA256
from Cryptodome.PublicKey import RSA
from Cryptodome.Signature import pkcs1_15
from lxml import etree
MOCK_DGCA_PRIVATE_KEY = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Resources", "dgca_private.pem")
MOCK_DGCA_CERTIFICATE = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Resources", "dgca.cert")



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


def sign_permission_artefact(xml_root, private_key=MOCK_DGCA_PRIVATE_KEY, certificate=MOCK_DGCA_CERTIFICATE):
    """
    Sign the permission artefact xml with the private key stored .
    Optionally pass a different key path to sign with a different key
    :param xml_root: the xml root object to sign
    :param private_key: the path to the private key to perform signing
    :return: the signed XML root object. Note - this needs to be saved as a file
    """
    root = xml_root.getroot()

    with open(private_key, 'rb') as f, open(certificate) as c:
        key = f.read()
        cert = c.read()
    signed_root = sx.XMLSigner()
    ns = {}
    ns[None] = signed_root.namespaces['ds']
    signed_root.namespaces = ns
    signed_root = signed_root.sign(root, key=key, cert=cert)
    return signed_root


def verify_xml_signature(xml_file, certificate_path):
    """
    Verify the signature of a given xml file against a certificate
    :param path xml_file: path to the xml file for verification
    :param certificate_path: path to the certificate to be used for verification
    :return: bool: the success of verification
    """
    # TODO -  refactor such that this verifies for generic stuff
    tree = etree.parse(xml_file)
    root = tree.getroot()
    with open(certificate_path) as f:
        certificate = f.read()
        # for per_tag in root.iter('UAPermission'):
        #     data_to_sign = per_tag
        try:
            verified_data = sx.XMLVerifier().verify(data=root, require_x509=True, x509_cert=certificate).signed_xml
            # The file signature is authentic
            return True
        except cryptography.exceptions.InvalidSignature:
            # print(verified_data)
            # add the type of exception
            return False


def verify_flight_log_signature_objs(log_object, public_key_obj):
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


def verify_flight_log_signature(flight_log, public_key):
    """
    wrapper for flight log verification using paths instead of in memory objects
    :param path flight_log: path JSON encoded NPNT compliant flight log
    :param path public_key: path to RSA 2048 public key pem file
    :return: bool: True or False on success of verification
    """
    with open(flight_log) as a, open(public_key) as b:
        return verify_flight_log_signature_objs(a.read(), b.read())


def sign_log(log_path, private_key_path, out_path=None):
    """
    sample function to demonstrate how to sign a flight log.
    This complements the verify_flight_log_signature methood
    :param log_path: path to log file to be signed
    :param private_key_path: path to the private key to be used for signing.
    :param out_path: path to save the signed log file -
            defaults to '-signed' added to it's name if no path is specified
    :return: None
    """
    with open(log_path, "rb") as log_obj, open(private_key_path) as key_ob:
        jd = json.loads(log_obj.read())
        rsa_key = RSA.import_key(key_ob.read())
        hashed_logdata = SHA256.new(bytes(str((jd['FlightLog'])).encode()))
        log_signature = pkcs1_15.new(rsa_key).sign(hashed_logdata)
        # the signature is encoded in base64 for transport
        enc = base64.b64encode(log_signature)
        # dealing with python's byte string expression
        jd['Signature'] = str(enc)[2:-1]
    if out_path:
        save_path = out_path
    else:
        save_path = log_path[:-5] + "-signed.json"
    with open(save_path, 'w') as outfile:
        json.dump(jd, outfile, indent=4)
    return save_path


def create_keys(folder, keyname):
    """
    create a RSA 2048 keypair
    :param folder: path to save the keypair
    :param str keyname: name of the key pair to save as keyname_private.pem,and keyname_public.pem
    :return:
    """
    key = RSA.generate(2048)
    private_key = key.export_key()
    with open(os.path.join(folder, keyname + "_private.pem"), "wb") as file_out:
        file_out.write(private_key)

    public_key = key.publickey().export_key()
    with open(os.path.join(folder, keyname + "_public.pem"), "wb") as file_out:
        file_out.write(public_key)
