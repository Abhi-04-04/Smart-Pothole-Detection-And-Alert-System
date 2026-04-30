
import numpy as np
import requests
from ultralytics import YOLO
from depth_estimator import DepthEstimator
from alert_manager import AlertManager
from gps_tracker import GPSTracker


class PotholeDetectionPipeline:

    def __init__(self, model_path: str):

        self.model = YOLO(model_path)

        self.depth_estimator = DepthEstimator()

        self.alert_manager = AlertManager()

        self.gps = GPSTracker()

        self.backend_url = (
            "https://pothole-detection-1-i67w.onrender.com/report_pothole"
        )

        self.auto_repair_url = (
            "https://pothole-detection-1-i67w.onrender.com/auto_repair_check"
        )

        self.frame_count = 0


    # --------------------------------------------------
    # Confidence-weighted severity scoring
    # --------------------------------------------------

    def compute_severity(
        self,
        normalized_depth,
        bbox_area_ratio,
        confidence
    ):

        severity_score = (
            normalized_depth * 0.5
            + bbox_area_ratio * 0.3
            + confidence * 0.2
        )

        if severity_score < 0.35:
            return "LOW"

        elif severity_score < 0.65:
            return "MEDIUM"

        else:
            return "HIGH"


    # --------------------------------------------------
    # Main detection pipeline
    # --------------------------------------------------

    def run_frame(self, frame):

        self.frame_count += 1

        SKIP = 2

        if self.frame_count % SKIP != 0:
            return frame, 0, "NONE"


        # Run YOLO detection

        results = self.model(
            frame,
            conf=0.25,
            iou=0.5,
            imgsz=480
        )

        annotated = results[0].plot()

        boxes = results[0].boxes

        count = len(boxes)

        severity = "NONE"


        # Get GPS once per frame

        latitude, longitude = self.gps.get_location()


        # --------------------------------------------------
        # Detection branch
        # --------------------------------------------------

        if count > 0:

            confidence = float(boxes.conf[0])

            depth_map = self.depth_estimator.estimate_depth(frame)

            x1, y1, x2, y2 = map(int, boxes.xyxy[0])

            bbox_area = (x2 - x1) * (y2 - y1)

            frame_area = frame.shape[0] * frame.shape[1]

            bbox_area_ratio = bbox_area / frame_area


            depth_region = depth_map[y1:y2, x1:x2]

            normalized_depth = (

                (depth_region.mean() - depth_map.min())

                / (depth_map.max() - depth_map.min() + 1e-6)

            )


            severity = self.compute_severity(
                normalized_depth,
                bbox_area_ratio,
                confidence
            )


            # Send detection to backend

            if latitude and longitude:

                payload = {

                    "latitude": latitude,

                    "longitude": longitude,

                    "severity": severity,

                    "confidence": confidence

                }

                try:

                    requests.post(
                        self.backend_url,
                        json=payload,
                        timeout=3
                    )

                except requests.RequestException:

                    pass


        # --------------------------------------------------
        # Nearby pothole alert system
        # --------------------------------------------------

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


        # --------------------------------------------------
        # Auto-repair lifecycle detection
        # --------------------------------------------------

        if count == 0 and self.frame_count % 5 == 0:

            if latitude and longitude:

                try:

                    requests.post(
                        self.auto_repair_url,
                        params={
                            "lat": latitude,
                            "lon": longitude
                        },
                        timeout=3
                    )

                except requests.RequestException:

                    pass


        return annotated, count, severity