from ultralytics import YOLO
import cv2

class PotholeDetector:

    def __init__(self, model_path):
        self.model = YOLO(model_path)

    def detect_image(self, image_path):

        results = self.model(image_path)

        for r in results:
            annotated = r.plot()

        return annotated