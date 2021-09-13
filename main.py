import json
import time
from types import SimpleNamespace
import requests
from datetime import date
import pygame
import configparser

from requests import ConnectionError
from requests import Timeout
from requests import  HTTPError


class VaccineInfo:

    def __init__(self, pin_code):
        self.pinCode = pin_code

    # Method to get data for vaccine centers at a given pin-code
    def getVaccineData(self):
        retries = 1
        success = False
        while not success:
            try:
                data = requests.get(
                    config.get('VaccineInfo', 'apiURL') + "?pincode=" + self.pinCode
                    + "&date=" + date.today().strftime("%d-%m-%Y"))

                centers = json.loads(data.text, object_hook=lambda d: SimpleNamespace(**d))
                return centers.centers
            except (ConnectionError, Timeout, HTTPError):
                time.sleep(10)
                retries += 1
                print("Retried", str(retries), "times.")


if __name__ == "__main__":
    # Load config from ini file
    config = configparser.ConfigParser()
    config.read(r'config.ini')

    # Initialize pygame mixer to play Alarm
    pygame.mixer.init()
    pygame.mixer.music.load(config.get('Alarm', 'alarmFile'))

    # Get the list of pin-codes configured in ini file
    pinCodeList = json.loads(config.get('Filters', 'pinCodes'))

    # We are not stopping until we do
    while True:
        for pinCode in pinCodeList:

            # Get the vaccine info for selected pin-code
            info = VaccineInfo(pinCode)
            for center in info.getVaccineData():

                # Filter the centres that don't have the required fee type
                if center.fee_type == config.get('Filters', 'feeType'):
                    for session in center.sessions:
                        print("Trying", center.name, center.pincode, "for", session.date + ".", "It is",
                              center.fee_type, "and has", session.available_capacity_dose2, "dose2 and",
                              session.available_capacity_dose1, "dose 1")

                        # Filter the centres that don't have the required amount of doses
                        if session.available_capacity_dose2 >= int(config.get('Filters', 'minimumDose2')) \
                                and session.available_capacity_dose1 >= int(config.get('Filters', 'minimumDose1')):
                            # Play the alarm sound and wait for a few seconds
                            pygame.mixer.music.play()
                            time.sleep(float(config.get('Alarm', 'alarmTime')))
        # Wait for a few seconds before pulling data again
        time.sleep(float(config.get('VaccineInfo', 'retryInSeconds')))
