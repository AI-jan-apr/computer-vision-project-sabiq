# Import required libraries
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from ultralytics import YOLO
import os, tempfile, random

# Create FastAPI app
app = FastAPI()

# Enable CORS (allow all origins - useful for frontend access)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Load YOLO model at startup
print("Loading model...")
model = YOLO("best.pt")
print("Model ready")

# Class labels mapping
CLASS_NAMES = {0: "crack", 1: "other", 2: "pothole"}

# Riyadh coordinate range (used for random location simulation)
RIYADH_LAT = (24.55, 24.85)
RIYADH_LNG = (46.55, 46.85)

# Generate random coordinates inside Riyadh
def random_riyadh():
    return round(random.uniform(*RIYADH_LAT), 6), round(random.uniform(*RIYADH_LNG), 6)

# Determine severity based on confidence and object size
def severity(conf, area):
    if conf > 0.85 and area > 0.05:
        return "high"
    elif conf > 0.65:
        return "medium"
    return "low"

# Check if uploaded file is an image
# "never trust the client"
def is_image(name):
    return name.lower().rsplit(".", 1)[-1] in ("jpg", "jpeg", "png", "bmp", "webp")

# Process image and return detections
def process_image(path):
    results = model.predict(source=path, conf=0.25, verbose=False)
    out = []
    for r in results:
        for box in r.boxes:
            cls   = int(box.cls)  # class id
            conf  = float(box.conf)  # confidence score
            xywhn = box.xywhn[0].tolist()  # normalized bounding box
            lat, lng = random_riyadh()  # random location
            out.append({
                "damage_type": CLASS_NAMES.get(cls, "other"),
                "confidence" : round(conf, 3),
                "severity"   : severity(conf, xywhn[2] * xywhn[3]),
                "bbox"       : xywhn,
                "frame"      : 0,
                "latitude"   : lat,
                "longitude"  : lng,
            })
    return out

# Process video using tracking (ByteTrack)
def process_video(path):
    results = model.track(
        source=path,
        conf=0.25,
        tracker="bytetrack.yaml",
        stream=True,
        verbose=False,
        save=False,
    )

    seen = {}  # store best detection per tracked object

    for frame_idx, r in enumerate(results):
        if r.boxes is None or r.boxes.id is None:
            continue

        # Loop through tracked objects
        for tid, cls, conf, xywhn in zip(
            r.boxes.id.int().tolist(),
            r.boxes.cls.int().tolist(),
            r.boxes.conf.tolist(),
            r.boxes.xywhn.tolist(),
        ):
            # Keep only the highest confidence detection per object
            if tid not in seen or conf > seen[tid]["confidence"]:
                lat = seen[tid]["latitude"] if tid in seen else random_riyadh()[0]
                lng = seen[tid]["longitude"] if tid in seen else random_riyadh()[1]
                seen[tid] = {
                    "damage_type": CLASS_NAMES.get(cls, "other"),
                    "confidence" : round(conf, 3),
                    "severity"   : severity(conf, xywhn[2] * xywhn[3]),
                    "bbox"       : xywhn,
                    "frame"      : frame_idx,
                    "latitude"   : lat,
                    "longitude"  : lng,
                }

    return list(seen.values())

# Root endpoint (health check)
@app.get("/")
def root():
    return {"status": "SABIQ API running"}

# Detection endpoint (image or video upload)
@app.post("/detect")
async def detect(file: UploadFile = File(...)):
    contents = await file.read()  # read uploaded file
    suffix   = "." + file.filename.split(".")[-1]  # get file extension

    # Save file temporarily
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(contents)
        tmp_path = tmp.name

    try:
        # Choose processing based on file type
        detections = process_image(tmp_path) if is_image(file.filename) else process_video(tmp_path)
    finally:
        os.unlink(tmp_path)  # delete temp file

    # Return results
    return {"total": len(detections), "detections": detections}
