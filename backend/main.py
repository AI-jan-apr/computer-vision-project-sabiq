from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from ultralytics import YOLO
from PIL import Image
import io, requests, os, tempfile
import cv2

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_URL = "https://huggingface.co/Rahaf2001/sabiq-road-detection/resolve/main/best.pt"

def download_model():
    if not os.path.exists("best.pt"):
        print("Downloading model...")
        r = requests.get(MODEL_URL)
        with open("best.pt", "wb") as f:
            f.write(r.content)
        print("✅ Model ready")

download_model()
model = YOLO("best.pt")

CLASS_NAMES = {
    0: 'crack',
    1: 'other',
    2: 'pothole'
}

def get_severity(conf, area):
    if conf > 0.85 and area > 0.05:
        return 'high'
    elif conf > 0.65:
        return 'medium'
    else:
        return 'low'

@app.get("/")
def root():
    return {"status": "SABIQ API running"}

@app.post("/detect")
async def detect(file: UploadFile = File(...)):
    contents = await file.read()
    filename = file.filename.lower()

    # ── فيديو ──
    if any(filename.endswith(ext) for ext in ['.mp4', '.avi', '.mov', '.mkv']):
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp:
            tmp.write(contents)
            tmp_path = tmp.name

        cap          = cv2.VideoCapture(tmp_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        # نحلل 5 frames موزعة على الفيديو
        sample_points  = [int(total_frames * i / 5) for i in range(1, 6)]
        all_detections = []

        for frame_num in sample_points:
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
            ret, frame = cap.read()
            if not ret:
                continue

            img     = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            results = model(img)

            for box in results[0].boxes:
                cls   = int(box.cls)
                conf  = float(box.conf)
                xywhn = box.xywhn[0].tolist()
                area  = xywhn[2] * xywhn[3]
                all_detections.append({
                    "damage_type": CLASS_NAMES.get(cls, 'other'),
                    "confidence" : round(conf, 3),
                    "severity"   : get_severity(conf, area),
                    "bbox"       : xywhn,
                    "frame"      : frame_num
                })

        cap.release()
        os.unlink(tmp_path)

        return {
            "total"     : len(all_detections),
            "detections": all_detections
        }

    # ── صورة ──
    else:
        try:
            img = Image.open(io.BytesIO(contents))
        except Exception as e:
            return {"error": str(e), "total": 0, "detections": []}

        results        = model(img)
        all_detections = []

        for box in results[0].boxes:
            cls   = int(box.cls)
            conf  = float(box.conf)
            xywhn = box.xywhn[0].tolist()
            area  = xywhn[2] * xywhn[3]
            all_detections.append({
                "damage_type": CLASS_NAMES.get(cls, 'other'),
                "confidence" : round(conf, 3),
                "severity"   : get_severity(conf, area),
                "bbox"       : xywhn,
                "frame"      : 0
            })

        return {
            "total"     : len(all_detections),
            "detections": all_detections
        }
