#!/usr/bin/env python3
"""
This script pulls the latest status from the Hyundai API for a given VIN and compares the results to the previous status.
If there are updates, they will be emailed to the user.

To use, update the constants below and run! This can be added as a cron job to run automatically.

PoC: deltakilojuliet on the www.ioniqforum.com
"""
import json
import requests
import smtplib

# Update these constants before your first run.
VIN_NUM = "Your_VIN"
NOTICE_ADDR = "your_email@gmail.com"
GMAIL_ADDR = "sender@gmail.com"
GMAIL_PWD = "app_specific_password"
STATUS_FILE = "status.txt"

class Status:
    """Object that contains functions to retrieve updates on your Ioniq5."""
    def __init__(self):
        """Constructor for the class."""
        self.status = self.load()
    
    def get_status(self):
        """
        Retrieves the status of the car from the Hyundai API

        Returns:
            A dictionary with the VIN, inventory status, and delivery date
        """
        # Fetch the JSON
        status_url = f"https://hyundai-custom-api.herokuapp.com/?vin={VIN_NUM}"
        res = requests.get(status_url)
        page = res.json()
        if len(page) != 1:
            print("VIN Not Found")
            return False
        # Parse the JSON
        record = page[0]["vehicle"][0]
        out_dict = {"vin": record["vin"], "status": record["inventoryStatus"], "delivery": record["plannedDeliveryDate"]}
        print(f"UPDTE: {out_dict}")
        return out_dict
    
    def diff(self, update):
        """
        Check the previous status against a new status. Any changes will be emailed.

        Args:
            update (dict): Dictionary containing the VIN, inventory status, and delivery date from the API

        Returns:
            True if successful
        """
        if self.status['status'] == update['status'] and self.status['delivery'] == update['delivery']:
            print("No Updates")
            return True
        elif self.status['status'] != update['status'] and self.status['delivery'] == update['delivery']:
            msg = f"Status changed from {self.status['status']} to {update['status']}"
        elif self.status['status'] == update['status'] and self.status['delivery'] != update['delivery']:
            msg = f"Delivery date changed from {self.status['delivery']} to {update['delivery']}"
        else:
            msg = f"Status changed from {self.status['status']} to {update['status']}\nDelivery date changed from {self.status['delivery']} to {update['delivery']}"
        print(msg)
        self._notify(msg)
        return True

    def load(self):
        """ Load the previous status JSON into the Status object."""
        out_file = open(STATUS_FILE, "r")
        data_dict = json.loads(out_file.readline())
        print(f"START: {data_dict}")
        out_file.close()
        return data_dict

    def _notify(self, content):
        """
        Emails the user updates.

        Args:
            content (str): The message to be sent in the body of the email
        """
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(GMAIL_ADDR, GMAIL_PWD)
        message = f"From: {GMAIL_ADDR}\nTO: {NOTICE_ADDR}\nSubject: Ioniq 5 Update\n\n{content}"
        server.sendmail(GMAIL_ADDR, NOTICE_ADDR, f"UPDATE: {message}")
        server.close()

    def save(self, data_dict):
        """ Save the new status JSON to file."""
        out_file = open(STATUS_FILE, "w")
        json.dump(data_dict, out_file)
        out_file.close()
    
if __name__ == "__main__":
    """ Run the script via command line."""
    stat_obj = Status()
    update = stat_obj.get_status()
    if update:
        stat_obj.diff(update)
        stat_obj.save(update)
