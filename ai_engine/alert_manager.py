import requests


class AlertManager:

    def __init__(self):

        # self.backend_url = "http://127.0.0.1:5000/nearby_potholes"
        self.backend_url = "http://127.0.0.1:8000/nearby_potholes"


    def check_alert(self, latitude, longitude):

        try:

            response = requests.get(
                self.backend_url,
                params={
                    "lat": latitude,
                    "lon": longitude
                }
            )

            potholes = response.json()

            return potholes

        except:

            return []