# SABIQ Model Weights

## Model Details
- **Architecture:** YOLOv26m
- **Dataset:** RDD2022 (Road Damage Detection)
- **Classes:** crack, other, pothole
- **mAP50:** 0.636
- **Epochs:** 65
- **Image Size:** 640

## Download
Model weights hosted on Hugging Face:
https://huggingface.co/Rahaf2001/sabiq-road-detection

## Usage
```python
from ultralytics import YOLO
model = YOLO("best.pt")
results = model("road_image.jpg", conf=0.25)
```

## API
Live inference API:
https://rahaf2001-sabiq-api.hf.space/detect
