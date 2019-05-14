# Digital Sky Provisional Testing App

A simple and easy tool to perform a basic check of NPNT/ Digital Sky compliance. 
The App is a checklist to verify basic NPNT work and is limited to NPNT verification, PA, PIN check and Flight log signature Verification. 

## Scope of Testing
The test is designed to be a double blind experiment to verify NPNT compliance.
The app generates permission artefacts for a specific location 
(subject to DGCA testing place approval). 
The application generates various permission artefacts for assessment in a random order. 
Both the applicant and the testing authority are unaware of which permission 
artefacts are intended to pass or fail. 

This double blind test ensures that the following are checked:
- Incorrect Geofence check
- Incorrect time limits check
- Bad Pilot PIN check 
- Spurious permission artefact check
- Valid Permission artefact check

## Validation
These five test scenarios are the ones which will be tested by the applicant.
After the observations of the RPAS behavior on all the scenarios are recorded,
the applicant proceeds to check the flight log generation.
The Flight log is generated on breaching the geofence set by a valid permission artefact.
The Digital signature of the Flight log is then verified against the public key of the drone.

## For Developers
The app is written in python 3. To run the app, download the repo or clone the repository using

`git clone https://github.com/iSPIRT/NPNT-Provisional-testing-tool.git`

install the requirements 

`pip install -r requirements.txt`

Run the app

`python npnt_testing_app.py`

### Sample Cases - 
#### Sign a Flight log using a public key
```python
from helpers import sign_log
sign_log(unisgned_log_file_path, sample)
``` 

