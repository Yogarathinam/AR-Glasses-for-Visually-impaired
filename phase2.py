import cv2
import queue
import time
import threading
import asyncio
import tempfile
import os
import sounddevice as sd
import soundfile as sf
import speech_recognition as sr
from ultralytics import YOLO
from google import genai
from google.genai import types
import edge_tts
import json

# --------------------------- CONFIG ---------------------------
GEMINI_API_KEY = "AIzaSyDvKHDYtSQWgWQOJow0yj0AFnWYGz98yIc"  # <-- your key
VOICE = "en-US-AriaNeural"
FRAME_RESIZE = (640, 480)
DETECTION_THRESHOLD = 0.5

# --------------------------- GLOBALS ---------------------------
frame_queue = queue.Queue()
running = True
tts_playing = False
tts_stop_flag = threading.Event()  # Flag to stop TTS immediately
system_prompt = """
You are an assistant for visually impaired users. 
You cannot see anything yourself; you can only rely on the JSON input provided to you, 
which describes the objects detected by a camera. 

The JSON will contain a list of objects with the following keys: 
- "name": the type of object
- "direction": relative direction to the user (e.g., "to your left", "right in front of you")
- "distance": approximate distance in centimeters

Your task is to respond only based on this JSON input. 
- Describe the scene in clear, concise, and helpful language.
- Give directions, distances, and warnings if objects are too close.
- Do not assume anything that is not in the JSON.
- Use simple language suitable for a visually impaired person.
- Always be polite, informative, and encouraging.

Example: 
Input JSON: [{"name": "chair", "direction": "to your right", "distance": 120}, {"name": "person", "direction": "right in front of you", "distance": 50}]
Response: "There is a person right in front of you, about 50 centimeters away. A chair is to your right at 1.2 meters."
"""

# --------------------------- TTS ---------------------------
async def speak(text):
    global tts_playing
    tts_playing = True
    tts_stop_flag.clear()
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            out_path = tmp.name
        tts = edge_tts.Communicate(text, VOICE)
        await tts.save(out_path)
        data, fs = sf.read(out_path, dtype='float32')

        sd.play(data, fs)
        while sd.get_stream().active:
            if tts_stop_flag.is_set():
                sd.stop()
                break
            time.sleep(0.1)
        os.remove(out_path)
    except Exception as e:
        print("TTS error:", e)
    tts_playing = False

def speak_thread(text):
    threading.Thread(target=lambda: asyncio.run(speak(text)), daemon=True).start()

# --------------------------- STT ---------------------------
def listen_for_command(mic_index):
    global tts_playing
    recognizer = sr.Recognizer()
    mic = sr.Microphone(device_index=mic_index)
    with mic as source:
        recognizer.adjust_for_ambient_noise(source)
        while tts_playing:
            time.sleep(0.1)  # Wait until TTS finishes
        print("🎤 Listening for command...")
        try:
            audio = recognizer.listen(source, timeout=5)
            query = recognizer.recognize_google(audio).lower()
            print(f"🗣️ You said: {query}")
            return query
        except Exception:
            return ""

# --------------------------- CAMERA ---------------------------
def camera_thread(cam_index):
    global running
    cap = cv2.VideoCapture(cam_index, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_RESIZE[0])
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_RESIZE[1])
    while running:
        ret, frame = cap.read()
        if ret:
            if not frame_queue.empty():
                try:
                    frame_queue.get_nowait()
                except queue.Empty:
                    pass
            frame_queue.put(frame)
        time.sleep(0.01)
    cap.release()

# --------------------------- OBJECT DETECTION ---------------------------
def detect_objects(model, frame):
    results = model(frame)
    detections = results[0].boxes.data.cpu().numpy() if results[0].boxes is not None else []
    frame_center_x = FRAME_RESIZE[0] / 2
    objects_found = []

    for det in detections:
        x1, y1, x2, y2, conf, cls = det
        if conf < DETECTION_THRESHOLD:
            continue
        cls_name = model.names[int(cls)].lower()
        obj_center_x = (x1 + x2) / 2
        direction_offset = obj_center_x - frame_center_x
        direction = "right in front of you" if abs(direction_offset) < 50 else ("to your left" if direction_offset < 0 else "to your right")
        width_px = x2 - x1
        distance = round(1000 / max(width_px, 1))
        objects_found.append({
            "name": cls_name,
            "direction": direction,
            "distance": distance
        })
    return objects_found

# --------------------------- GEMINI ---------------------------
def ask_gemini(user_query, detected_objects):
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    obj_summary = json.dumps(detected_objects) if detected_objects else "[]"
    prompt = f"{system_prompt}\nDetected objects JSON: {obj_summary}\nUser asked: '{user_query}'"
    print("\n📨 Gemini Request:")
    print(prompt)

    contents = [types.Content(role="user", parts=[types.Part(text=prompt)])]
    generate_config = types.GenerateContentConfig(response_modalities=["TEXT"])

    response_text = ""
    try:
        for chunk in client.models.generate_content_stream(
            model="gemini-2.5-flash-lite",
            contents=contents,
            config=generate_config
        ):
            if chunk.candidates and chunk.candidates[0].content and chunk.candidates[0].content.parts:
                text_part = chunk.candidates[0].content.parts[0].text
                if text_part:
                    print(text_part)
                    response_text += text_part
    except Exception as e:
        print("❌ Gemini API error:", e)
        response_text = "Sorry, I couldn't get a response."
    return response_text

# --------------------------- MAIN ---------------------------
def main():
    global running
    cam_index = int(input("Enter camera index: "))
    mic_index = int(input("Enter microphone index: "))
    model = YOLO("yolov8n.pt")

    threading.Thread(target=camera_thread, args=(cam_index,), daemon=True).start()
    print("✅ Ready! Speak your command...")

    while running:
        query = listen_for_command(mic_index)
        if not query:
            continue

        if query in ["exit", "quit", "stop"]:
            tts_stop_flag.set()        # Stop any ongoing TTS
            speak_thread("Shutting down.")
            running = False
            break

        frame = frame_queue.get() if not frame_queue.empty() else None
        detected_objects = detect_objects(model, frame) if frame is not None else []
        response_text = ask_gemini(query, detected_objects)
        speak_thread(response_text)

# --------------------------- RUN ---------------------------
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Exiting system.")
        running = False
        tts_stop_flag.set()  # Stop any ongoing TTS
