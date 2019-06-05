import os
import sys
from random import shuffle

from PyQt5 import QtGui
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QMessageBox

from helpers import verify_flight_log_signature_objs
from permissions import generate_all_test_permission_artefacts, \
    generate_valid_permission

INCORRECT_COORDS = [[-39.375,19.973348786110602],[-45.3515625,11.178401873711785],[-28.125,8.407168163601076],[-39.375,19.973348786110602]]
COORDS = [[77.609316, 12.934158], [77.609852, 12.934796],[77.610646, 12.934183], [77.610100, 12.933551], [77.609316,12.934158]]  # 
# use a private key as a fake public key

class AppWindow(QDialog):
    def __init__(self):
        super(AppWindow, self).__init__()
        self.drone_id_widget = None
        self.upload_key_widget = None
        self.generate_permission_buttonwidget = None
        self.permissions_window = None
        self.verify_results_buttonwidget = None

        # required vars
        self.drone_public_key = None
        self.permission_cases = []
        self.permission_case_truth = []
        self.responses = [None, None, None, None, None]
        self.log_file = None
        self.breachtest_passed = None

        # Init guiwidgets and windows
        self.create_drone_id_widget()
        self.create_key_upload_widget()
        self.create_permission_gen_btn()
        self.create_permission_tests_window()
        self.create_verify_and_reset_row()

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.drone_id_widget)
        main_layout.addWidget(self.upload_key_widget)
        main_layout.addWidget(self.generate_permission_buttonwidget)
        main_layout.addWidget(self.permissions_window)
        main_layout.addWidget(self.verify_results_buttonwidget)
        self.setLayout(main_layout)
        self.setWindowTitle("NPNT Provisional Testing App")
        self.permissions_window.hide()
        self.verify_results_buttonwidget.hide()

    def create_drone_id_widget(self):
        self.drone_id_entry = QLineEdit(self)
        drone_id = QLabel()
        drone_id.setText("Input Drone ID: ")
        self.drone_id_widget = QWidget()

        layout = QHBoxLayout()
        layout.addWidget(drone_id)
        layout.addWidget(self.drone_id_entry)
        self.drone_id_widget.setLayout(layout)

    def create_key_upload_widget(self):

        self.upload_key_widget = QWidget()
        self.upload_key_widget.resize(self.upload_key_widget.sizeHint())

        self.drone_key_label = QLabel()
        self.drone_key_label.hide()
        self.drone_key_label.setText("Drone Key Uploaded!")

        layout = QHBoxLayout()
        self.upload_drone_key_btn = QPushButton("Upload Drone Key")
        self.upload_drone_key_btn.clicked.connect(self.drone_key_browser)
        layout.addWidget(self.upload_drone_key_btn)
        layout.addWidget(self.drone_key_label)

        self.upload_key_widget.setLayout(layout)

    def create_permission_gen_btn(self):

        self.generate_permission_buttonwidget = QWidget()
        self.generate_permission_buttonwidget.resize(
            self.generate_permission_buttonwidget.sizeHint())

        layout = QHBoxLayout()
        self.generate_tests_button = QPushButton("Generate Test cases")
        self.generate_tests_button.clicked.connect(
            self.check_inputs_and_create_tests)

        layout.addWidget(self.generate_tests_button)
        self.generate_permission_buttonwidget.setLayout(layout)

    def create_permission_tests_window(self):

        self.permissions_window = QWidget()
        download_icon = QtGui.QPixmap('Resources/download_1.png')
        row_0_widget = QWidget()
        row_0 = QHBoxLayout()
        header = QLabel("Drone Armed:")
        header.setAlignment(Qt.AlignRight)
        header.setIndent(10)
        row_0.addWidget(header)
        row_0_widget.setLayout(row_0)

        row_1_widget = QWidget()
        row_1 = QHBoxLayout()
        pa_1 = QLabel("Test 1")
        pa_1_download_button = QPushButton()
        pa_1_download_button.setText("Download PA")
        pa_1_download_button.setIcon(QtGui.QIcon(download_icon))
        pa_1_download_button.clicked.connect(
            lambda: self.save_permission_artefact(0))

        self.pass_1 = QRadioButton("Yes")
        self.fail_1 = QRadioButton("No")
        self.pass_1.toggled.connect(
            lambda: self.update_responses(self.pass_1, 0))
        self.fail_1.toggled.connect(
            lambda: self.update_responses(self.fail_1, 0))

        row_1.addWidget(pa_1)
        row_1.addWidget(pa_1_download_button)
        row_1.addWidget(self.pass_1)
        row_1.addWidget(self.fail_1)
        row_1_widget.setLayout(row_1)

        row_2_widget = QWidget()
        row_2 = QHBoxLayout()
        pa_2 = QLabel("Test 2")
        pa_2_download_button = QPushButton()
        pa_2_download_button.setText("Download PA")
        pa_2_download_button.setIcon(QtGui.QIcon(download_icon))
        pa_2_download_button.clicked.connect(
            lambda: self.save_permission_artefact(1))

        self.pass_2 = QRadioButton("Yes")
        self.fail_2 = QRadioButton("No")
        self.pass_2.toggled.connect(
            lambda: self.update_responses(self.pass_2, 1))
        self.fail_2.toggled.connect(
            lambda: self.update_responses(self.fail_2, 1))

        row_2.addWidget(pa_2)
        row_2.addWidget(pa_2_download_button)
        row_2.addWidget(self.pass_2)
        row_2.addWidget(self.fail_2)
        row_2_widget.setLayout(row_2)

        row_3_widget = QWidget()
        row_3 = QHBoxLayout()
        pa_3 = QLabel("Test 3")
        pa_3_download_button = QPushButton()
        pa_3_download_button.setText("Download PA")
        pa_3_download_button.setIcon(QtGui.QIcon(download_icon))
        pa_3_download_button.clicked.connect(
            lambda: self.save_permission_artefact(2))

        # TODO -  rename all the pass/fail to Armed/ Disarmed
        self.pass_3 = QRadioButton("Yes")
        self.fail_3 = QRadioButton("No")
        self.pass_3.toggled.connect(
            lambda: self.update_responses(self.pass_3, 2))
        self.fail_3.toggled.connect(
            lambda: self.update_responses(self.fail_3, 2))
        row_3.addWidget(pa_3)
        row_3.addWidget(pa_3_download_button)
        row_3.addWidget(self.pass_3)
        row_3.addWidget(self.fail_3)
        row_3_widget.setLayout(row_3)

        row_4_widget = QWidget()
        row_4 = QHBoxLayout()
        pa_4 = QLabel("Test 4")
        pa_4_download_button = QPushButton()
        pa_4_download_button.setText("Download PA")
        pa_4_download_button.setIcon(QtGui.QIcon(download_icon))
        pa_4_download_button.clicked.connect(
            lambda: self.save_permission_artefact(3))

        self.pass_4 = QRadioButton("Yes")
        self.fail_4 = QRadioButton("No")
        self.pass_4.toggled.connect(
            lambda: self.update_responses(self.pass_4, 3))
        self.fail_4.toggled.connect(
            lambda: self.update_responses(self.fail_4, 3))
        row_4.addWidget(pa_4)
        row_4.addWidget(pa_4_download_button)
        row_4.addWidget(self.pass_4)
        row_4.addWidget(self.fail_4)
        row_4_widget.setLayout(row_4)

        row_5_widget = QWidget()
        row_5 = QHBoxLayout()
        pa_5 = QLabel("Test 5")
        pa_5_download_button = QPushButton()
        pa_5_download_button.setText("Download PA")
        pa_5_download_button.setIcon(QtGui.QIcon(download_icon))
        pa_5_download_button.clicked.connect(
            lambda: self.save_permission_artefact(4))

        self.pass_5 = QRadioButton("Yes")
        self.fail_5 = QRadioButton("No")
        self.pass_5.toggled.connect(
            lambda: self.update_responses(self.pass_5, 4))
        self.fail_5.toggled.connect(
            lambda: self.update_responses(self.fail_5, 4))
        row_5.addWidget(pa_5)
        row_5.addWidget(pa_5_download_button)
        row_5.addWidget(self.pass_5)
        row_5.addWidget(self.fail_5)
        row_5_widget.setLayout(row_5)

        row_6_widget = QWidget()
        row_6 = QHBoxLayout()
        breach_test = QLabel("Breach Test")
        row_6_download_button = QPushButton()
        row_6_download_button.setText("Download PA")
        row_6_download_button.setIcon(QtGui.QIcon(download_icon))
        row_6_download_button.clicked.connect(
            lambda: self.save_permission_artefact(valid_pa=True))
        self.upload_log = QPushButton("Upload Log")
        self.upload_log.clicked.connect(lambda: self.upload_log_browser())
        row_6.addWidget(breach_test)
        row_6.addWidget(row_6_download_button)
        row_6.addWidget(self.upload_log)
        row_6_widget.setLayout(row_6)

        main_layout = QVBoxLayout()
        main_layout.addWidget(row_0_widget)
        main_layout.addWidget(row_1_widget)
        main_layout.addWidget(row_2_widget)
        main_layout.addWidget(row_3_widget)
        main_layout.addWidget(row_4_widget)
        main_layout.addWidget(row_5_widget)
        main_layout.addWidget(row_6_widget)

        self.permissions_window.setLayout(main_layout)

    def save_permission_artefact(self, index=None, valid_pa=False):
        if valid_pa:
            index = 5
            current_perm_xml = generate_valid_permission(
                self.drone_id_entry.text(), self.drone_public_key, COORDS)
        else:
            current_perm_xml = self.permission_cases[index]
        folder = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        save_path = os.path.join(folder,
                                 'signed_permission_artefact_{}.xml'.format(
                                     index + 1))

        from lxml import etree
        etree.ElementTree(current_perm_xml).write(save_path)

    def update_responses(self, btn, index):
        if btn.text() == "Yes":
            self.responses[index] = btn.isChecked()
        if btn.text() == "No":
            self.responses[index] = not(btn.isChecked())

    def create_verify_and_reset_row(self):

        self.verify_results_buttonwidget = QWidget()
        self.verify_results_buttonwidget.resize(
            self.generate_permission_buttonwidget.sizeHint())

        layout = QHBoxLayout()
        verify_results_button = QPushButton("Verify Results")
        verify_results_button.setToolTip(
            "Click to verify the testing results to check if the application clears or fails.")
        verify_results_button.clicked.connect(self.check_and_verify_results)

        reset_btn = QPushButton("Reset")
        reset_btn.setToolTip("Click to Reset the app.")
        reset_btn.clicked.connect(lambda: self.reset_window())

        layout.addWidget(reset_btn)
        layout.addWidget(verify_results_button)
        self.verify_results_buttonwidget.setLayout(layout)

    def check_and_verify_results(self):
        # show warnings for incomplete inputs
        if self.log_file is None:
            self.show_warning("Please Upload the flight log for verification")
            return
        elif None in self.responses:
            self.show_warning("Please Upload the flight log for verification")
            return

        try:
            log = open(self.log_file, "rb").read()
            self.flight_log_sign_verified = verify_flight_log_signature_objs(log,
                                                                             self.drone_public_key)
        except Exception as e:
            self.show_warning(
                "Incorrect file format. Signature verification failed/n"
                "Check input file format and specification", str(e))
            return
        self.correct_responses = self.permission_case_truth == self.responses
        tests_passed = self.correct_responses and self.flight_log_sign_verified

        if tests_passed:
            self.show_success_dialog()
        elif not self.correct_responses:
            response_results = [
                "Passed" if (x == y) else "Failed - Incorrect Response" for x, y
                in zip(self.permission_case_truth, self.responses)]
            test_nums = ["Test {} result : ".format(x) for x in range(1, 6)]
            response_text = "\n".join(
                x + y for x, y in zip(test_nums, response_results))
            self.show_failure_dialog(
                "Responses did not match.\n\n{}".format(response_text))
        elif not self.flight_log_sign_verified:
            self.show_failure_dialog("Flight log signature did not match")
        self.reset_window()

    def check_inputs_and_create_tests(self):
        if self.drone_id_entry.text() == '':
            error_msg = "please input Drone ID"
            detail_err = "Drone ID is the internal ID of the unmanned Aircraft"
            self.show_warning(error_msg, detail_err)
        elif self.drone_public_key is None:
            error_msg = "please upload Drone Public  key"
            detail_err = "Public key is required for generation of PA"
            self.show_warning(error_msg, detail_err)
        else:
            # create the permissions
            self.permissions_window.show()
            self.verify_results_buttonwidget.show()
            self.generate_tests_button.setText("Re - Generate Test Cases")
            self.setup_test_scenarios()

    def setup_test_scenarios(self):
        # Setup the test cases. shuffle them to ensure double blind randomness.
        cases = generate_all_test_permission_artefacts(
            self.drone_id_entry.text(), self.drone_public_key, COORDS, INCORRECT_COORDS)
        shuffle(cases)
        # reset truth cases to make sure that we dont have a overflowing list
        self.permission_case_truth = []
        # cases have now been shuffled in order
        for index, key in enumerate(cases):
            self.permission_case_truth.append(key['expected_result'])
            self.permission_cases.append(key['permission'])

    def show_failure_dialog(self, fail_msg=''):
        """
        A generic window to show failure of the test cases
        """
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)

        msg.setText("Test Result: Provisional NPNT test failed")
        msg.setInformativeText(fail_msg)
        msg.setWindowTitle("Test Result")
        msg.setStandardButtons(QMessageBox.Ok)

        msg.exec_()

    def show_success_dialog(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)

        msg.setText("Test Result: Pass")
        msg.setInformativeText("Provisional NPNT test passed")
        msg.setWindowTitle("Test Result")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def drone_key_browser(self):
        proceed = True
        drone_key_input, _filter = QFileDialog.getOpenFileName(self,
                                                               "Select RSA 2048 public key of RPAS",
                                                               filter='*.pem')
        if not self.verify_keyin(drone_key_input):
            error_msg = "Public key is incorrect or not uploaded"
            detailed_error = " The public key should eb a RSA 2048 key"
            self.show_warning(error_msg, detailed_error)
            proceed = False
        if proceed:
            self.drone_key_label.show()
            self.upload_drone_key_btn.setEnabled(False)

    def upload_log_browser(self):
        self.log_file, _filter = QFileDialog.getOpenFileName(self,
                                                             "Select test flight log")
        self.upload_drone_key_btn.setText('Flight log uploaded')

    def reset_window(self):
        """
        Reset the window to start from scratch again.
        """
        self.drone_id_entry.setText('')
        self.drone_key_label.hide()
        self.upload_drone_key_btn.setText('Upload New Drone key')
        self.upload_drone_key_btn.setEnabled(True)

        self.drone_public_key = None
        self.permission_cases = []
        self.permission_case_truth = []
        self.responses = [None, None, None, None, None]
        self.permissions_window.hide()
        self.verify_results_buttonwidget.hide()
        self.breachtest_passed = False

        # Reset button states-  hardcoded method - Refactor Later
        self.pass_1.setAutoExclusive(False)
        self.fail_1.setAutoExclusive(False)
        self.pass_2.setAutoExclusive(False)
        self.fail_2.setAutoExclusive(False)
        self.pass_3.setAutoExclusive(False)
        self.fail_3.setAutoExclusive(False)
        self.pass_4.setAutoExclusive(False)
        self.fail_4.setAutoExclusive(False)
        self.pass_5.setAutoExclusive(False)
        self.fail_5.setAutoExclusive(False)

        self.pass_1.setChecked(False)
        self.fail_1.setChecked(False)
        self.pass_2.setChecked(False)
        self.fail_2.setChecked(False)
        self.pass_3.setChecked(False)
        self.fail_3.setChecked(False)
        self.pass_4.setChecked(False)
        self.fail_4.setChecked(False)
        self.pass_5.setChecked(False)
        self.fail_5.setChecked(False)

        self.pass_1.setAutoExclusive(True)
        self.fail_1.setAutoExclusive(True)
        self.pass_2.setAutoExclusive(True)
        self.fail_2.setAutoExclusive(True)
        self.pass_3.setAutoExclusive(True)
        self.fail_3.setAutoExclusive(True)
        self.pass_4.setAutoExclusive(True)
        self.fail_4.setAutoExclusive(True)
        self.pass_5.setAutoExclusive(True)
        self.fail_5.setAutoExclusive(True)

        self.adjustSize()

    def verify_keyin(self, public_key_path):
        """
        Verify that the public key input is correct. Raise error if the file is
        not a public key.
        :param public_key_path: path to the public key file
        :return bool: success or fail of key path
        """
        if os.path.exists(public_key_path) and public_key_path.lower().endswith('.pem'):
            # TODO -verify that this is a public key
            with open(public_key_path) as f:
                self.drone_public_key = f.read()
            return True
        else:
            return False

    def show_warning(self, warning_message, detailed_error=None):
        """
        Generic Warning dialog. Adds detailed error if required
        """
        warn = QMessageBox()
        warn.setIcon(QMessageBox.Warning)
        warn.setText(warning_message)
        warn.setWindowTitle("Warning")
        warn.setStandardButtons(QMessageBox.Ok)
        if detailed_error is not None:
            warn.setDetailedText(detailed_error)
        warn.exec_()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet("")
    w = AppWindow()
    # TODO - create a stylesheet to make the app look better
    w.show()
    sys.exit(app.exec_())
