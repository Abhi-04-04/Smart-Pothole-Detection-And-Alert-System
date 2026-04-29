from ultralytics import YOLO
from depth_estimator import DepthEstimator
from alert_manager import AlertManager
from gps_tracker import GPSTracker

import requests
import numpy as np


class PotholeDetectionPipeline:

    def __init__(self, model_path: str):

        # Load YOLO pothole detection model
        self.model = YOLO(model_path)

        # Load depth estimation model (MiDaS)
        self.depth_estimator = DepthEstimator()

        # Nearby pothole alert system
        self.alert_manager = AlertManager()

        # GPS tracker
        self.gps = GPSTracker()

        # Backend API endpoint
        self.backend_url = "http://127.0.0.1:8000/report_pothole"
        # self.backend_url = "http://127.0.0"

        # Frame skipping counter (for performance)
        self.frame_count = 0


    def compute_severity(self, normalized_depth):

        """
        Convert depth value into severity level
        """

        if normalized_depth < 0.35:
            return "LOW"

        elif normalized_depth < 0.65:
            return "MEDIUM"

        else:
            return "HIGH"


    def run_frame(self, frame):

        """
        Real-time pothole detection pipeline

        Includes:
        - YOLO detection
        - Depth-based severity estimation
        - GPS tagging
        - Backend database update
        - Nearby pothole alerts
        - Auto repair detection lifecycle tracking
        """

        self.frame_count += 1
        SKIP = 2

        # Skip frames to improve FPS
        if self.frame_count % SKIP != 0:
            return frame, 0, "NONE"


        # -----------------------------
        # Run YOLO detection
        # -----------------------------

        results = self.model(frame, conf=0.25, iou=0.5, imgsz=480)

        annotated = results[0].plot()

        boxes = results[0].boxes

        count = len(boxes)

        severity = "NONE"


        # -----------------------------
        # If pothole detected
        # -----------------------------

        if count > 0:

            depth_map = self.depth_estimator.estimate_depth(frame)

            x1, y1, x2, y2 = map(int, boxes.xyxy[0])

            depth_region = depth_map[y1:y2, x1:x2]

            normalized_depth = (
                (depth_region.mean() - depth_map.min())
                / (depth_map.max() - depth_map.min() + 1e-6)
            )

            severity = self.compute_severity(normalized_depth)


            # -----------------------------
            # Send detection to backend
            # -----------------------------

            latitude, longitude = self.gps.get_location()

            if latitude and longitude:

                payload = {

                    "latitude": latitude,
                    "longitude": longitude,
                    "severity": severity

                }

                try:

                    requests.post(
                        self.backend_url,
                        json=payload
                    )

                except:

                    pass


        # -----------------------------
        # Nearby pothole alert system
        # -----------------------------

        latitude, longitude = self.gps.get_location()

        if latitude and longitude:

            nearby = self.alert_manager.check_alert(
                latitude,
                longitude
            )

            if nearby:

                print("WARNING: Pothole ahead!")

                for pothole in nearby:

                    print(
                        f"Severity: {pothole['severity']} | "
                        f"Distance: {pothole['distance']} meters"
                    )


        # -----------------------------
        # Auto-repair lifecycle detection
        # -----------------------------

        if count == 0 and self.frame_count % 5 == 0:

            latitude, longitude = self.gps.get_location()

            if latitude and longitude:

                try:

                    requests.post(

                        "http://127.0.0.1:8000/auto_repair_check",
                        # "http://127.0.0",

                        params={
                            "lat": latitude,
                            "lon": longitude
                        }

                    )

                except:

                    pass


        return annotated, count, severity