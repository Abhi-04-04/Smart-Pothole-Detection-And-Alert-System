import cv2
from ai_engine.pipeline import PotholeDetectionPipeline


pipeline = PotholeDetectionPipeline(
    model_path="runs/detect/train10/weights/best_finetuned.pt"
)


video_path = r"C:\Users\abhir\Downloads\Pathhole_project\ai_engine\Pathole_vedio.mp4"
cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    print("Error: Cannot open video file")
    exit()
print("Video opened successfully")

# cap = cv2.VideoCapture(0)
# if not cap.isOpened():
#     print("Error: Cannot access webcam")
#     exit()

# 🔹 store last detection results (important for smooth display)
last_count = 0
last_severity = "NONE"


while True:

    ret, frame = cap.read()

    if not ret:
        break


    output, count, severity = pipeline.run_frame(frame)


    # 🔹 update values only when detection exists
    if count != 0:
        last_count = count
        last_severity = severity


    cv2.putText(output,
                f"Potholes: {last_count}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2)


    cv2.putText(output,
                f"Severity: {last_severity}",
                (10, 70),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 0, 255),
                2)


    cv2.imshow("Smart Pothole Detection", output)


    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


cap.release()
cv2.destroyAllWindows()