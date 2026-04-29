import csv
from datetime import datetime


class PotholeDatabase:

    def __init__(self):

        self.filename = "pothole_database.csv"

        self.initialize_database()


    def initialize_database(self):

        try:
            with open(self.filename, "x", newline="") as file:

                writer = csv.writer(file)

                writer.writerow([
                    "timestamp",
                    "latitude",
                    "longitude",
                    "severity"
                ])

        except FileExistsError:

            pass


    def save_entry(self, latitude, longitude, severity):

        with open(self.filename, "a", newline="") as file:

            writer = csv.writer(file)

            writer.writerow([
                datetime.now(),
                latitude,
                longitude,
                severity
            ])