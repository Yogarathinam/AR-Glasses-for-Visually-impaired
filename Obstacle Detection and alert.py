import cv2
import asyncio
import edge_tts
from ultralytics import YOLO
import time
import pygame
import tempfile
import os

# Function to find working camera
def get_camera_index(max_tested=5):
    for i in range(max_tested):
        cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
        if cap.isOpened():
            cap.release()
            return i
    return None

# Find a camera
cam_index = get_camera_index()
if cam_index is None:
    print("❌ No working camera found!")
    exit()
else:
    print(f"✅ Using camera index {cam_index}")

# Load YOLOv8 nano model (fastest)
model = YOLO("yolov8n.pt")

# Setup camera
cap = cv2.VideoCapture(cam_index, cv2.CAP_DSHOW)

# Init pygame once (audio only)
pygame.mixer.init()

# ✅ TTS function (non-blocking, no overlap)
async def tts_to_file(text, out_path):
    communicate = edge_tts.Communicate(text, "en-US-AriaNeural")
    with open(out_path, "wb") as f:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])

def speak(text):
    # Stop old playback
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.stop()

    # Create temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmpfile:
        temp_path = tmpfile.name

    # Generate TTS (blocking for simplicity here)
    asyncio.run(tts_to_file(text, temp_path))

    # Play
    pygame.mixer.music.load(temp_path)
    pygame.mixer.music.play()

    # Cleanup after playback finishes
    def cleanup():
        try:
            os.remove(temp_path)
        except:
            pass

    # Poll until playback finishes
    while pygame.mixer.music.get_busy():
        pygame.time.wait(100)
    cleanup()

# Rough distance estimation based on bounding box width
def estimate_distance(bbox_width, frame_width):
    ratio = bbox_width / frame_width
    if ratio > 0.5:
        return 0.5
    elif ratio > 0.3:
        return 1
    elif ratio > 0.15:
        return 2
    else:
        return 3  # meters (approx)

last_alert_time = 0
alert_cooldown = 2  # seconds

while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ Failed to grab frame")
        break

    # Run YOLO inference
    results = model(frame, stream=True)

    closest_obj = None
    closest_dist = float("inf")
    frame_h, frame_w = frame.shape[:2]

    for r in results:
        for box in r.boxes:
            cls_id = int(box.cls[0])
            label = model.names[cls_id]
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            conf = float(box.conf[0])

            # Draw bounding box
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0,255,0), 2)
            cv2.putText(frame, f"{label} {conf:.2f}", (int(x1), int(y1)-5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)

            # Estimate distance
            bbox_w = x2 - x1
            dist = estimate_distance(bbox_w, frame_w)

            if dist < closest_dist:
                closest_dist = dist
                closest_obj = label

    # Trigger audio alert
    if closest_obj and (time.time() - last_alert_time > alert_cooldown):
        alert_text = f"{closest_obj} ahead, about {closest_dist} meters"
        print(alert_text)
        speak(alert_text)  # no more crash, no overlap
        last_alert_time = time.time()

    cv2.imshow("Obstacle Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
