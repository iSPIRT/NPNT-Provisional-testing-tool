import argparse
import sys
import os
from permissions import generate_all_test_permission_artefacts, \
    generate_valid_permission
from random import shuffle
import tempfile
from lxml import etree
import shutil
from zipfile import ZipFile
import pickle 

class BundleGenerator:
    def __init__(self, args):
        self.args = args

    def get_all_file_paths(self, directory): 
    
        # initializing empty file paths list 
        file_paths = [] 
    
        # crawling through directory and subdirectories 
        for root, directories, files in os.walk(directory): 
            for filename in files: 
                # join the two strings in order to form the full filepath. 
                filepath = os.path.join(root, filename) 
                file_paths.append(filepath) 
    
        # returning all file paths 
        return file_paths   

    def main(self):
        drone_public_key = self.args.key.read()
        cases = generate_all_test_permission_artefacts(
            self.args.id, drone_public_key)
        shuffle(cases)

        dirh = tempfile.mkdtemp()

        arr = []
        for case in enumerate(cases):
            p = os.path.join(dirh, 'permission_artifact_' + str(case[0] + 1) + '.xml')
            etree.ElementTree(case[1]['permission']).write(p)
            arr.append({
                "expected_result": case[1]['expected_result'],
                "test": case[1]['test']
            })

        breach_perm_xml = generate_valid_permission(
                self.args.id, drone_public_key)
        p = os.path.join(dirh, 'permission_artifact_breach.xml')
        etree.ElementTree(breach_perm_xml).write(p)

        file_paths = self.get_all_file_paths(dirh) 
        with ZipFile(self.args.bundle.name, 'w') as zip: 
            # writing each file one by one 
            for file in file_paths: 
                zip.write(file, arcname=os.path.basename(file)) 
        shutil.rmtree(dirh)

        thisdict =	{
            "cases": arr,
            "drone_id": self.args.id,
            "drone_public_key": drone_public_key
        }

        #truth file
        pickle.dump(thisdict, self.args.truth)
   
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--id', help='Drone ID', required=True)
    parser.add_argument('--key', help='Public key', type=argparse.FileType('r'), required=True)
    parser.add_argument('--bundle', help='Output testcase bundle', type=argparse.FileType('w'), required=True)
    parser.add_argument('--truth', help='Truth file for the bundle', type=argparse.FileType('wb'), required=True)
    args = parser.parse_args()
    gen = BundleGenerator(args)
    gen.main()