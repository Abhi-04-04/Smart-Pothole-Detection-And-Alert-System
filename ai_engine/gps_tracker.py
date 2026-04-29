import geocoder

class GPSTracker:

    def get_location(self):

        try:

            g = geocoder.ip("me")

            if g.ok:

                return g.latlng

        except:

            pass


        # fallback default location (Thiruvananthapuram example)
        print("⚠️ GPS unavailable. Using fallback location.")

        return 8.5241, 76.9366