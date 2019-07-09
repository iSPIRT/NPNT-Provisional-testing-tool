import argparse
import sys
import os
from permissions import generate_all_test_permission_artefacts, \
    generate_valid_permission
from helpers import verify_flight_log_signature_objs
from random import shuffle
import tempfile
from lxml import etree
import shutil
from zipfile import ZipFile
import pickle 
import xml.etree.ElementTree as ET
import json

class VerifyResults:
    def __init__(self, args):
        self.args = args

    def main(self):
        thisdict = pickle.load(self.args.truth)

        cases = []
        for elem in enumerate(thisdict['cases']):
            cases.append({
                "expected_result": elem[1]['expected_result'],
                "test": elem[1]['test']
            })
        drone_public_key = thisdict['drone_public_key']
        #drone_id = thisdict['drone_id']

        results = [
            {"test": cases[0]['test'], "passed": False},
            {"test": cases[1]['test'], "passed": False},
            {"test": cases[2]['test'], "passed": False},
            {"test": cases[3]['test'], "passed": False},
            {"test": "breach", "passed": False}
        ]

        #Case 1
        if(cases[0]['expected_result'] ==  self.args.s1):
            results[0]['passed'] = True

        #Case 2
        if(cases[1]['expected_result'] ==  self.args.s2):
            results[1]['passed'] = True

        #Case 3
        if(cases[2]['expected_result'] ==  self.args.s3):
            results[2]['passed'] = True

        #Case 4
        if(cases[3]['expected_result'] ==  self.args.s4):
            results[3]['passed'] = True

        #breach
        breach_log = self.args.breach_log.read()
        breach_passed = verify_flight_log_signature_objs(breach_log, drone_public_key)
        results[4]['passed'] = breach_passed

        #report
        self.args.report.write(json.dumps(results))
        
        print(results)
   
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--truth', help='Truth file for the bundle', type=argparse.FileType('rb'), required=True)
    parser.add_argument('--s1', help='Permission artifact 1 arm status', type=int, required=True)
    parser.add_argument('--s2', help='Permission artifact 2 arm status', type=int, required=True)
    parser.add_argument('--s3', help='Permission artifact 3 arm status', type=int, required=True)
    parser.add_argument('--s4', help='Permission artifact 4 arm status', type=int, required=True)
    parser.add_argument('--breach_log', help='Breach log file', type=argparse.FileType('r'), required=True)
    parser.add_argument('--report', help='Report file', type=argparse.FileType('w'), required=True)
    args = parser.parse_args()
    ver = VerifyResults(args)
    ver.main()