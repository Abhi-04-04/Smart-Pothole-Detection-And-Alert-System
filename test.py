from ai_engine.detector import potholeDetector

detector = potholeDetector("Yolov8")
detector.load_model()
print(detector.detect("test_image.jpg"))