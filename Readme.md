[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/nSn4fJNC)
<div align="center">

<img src="logo.png" alt="SABIQ Logo" width="200"/>

# SABIQ — سابق

**Proactive Road Damage Detection for Riyadh Municipality**

AI-powered system that detects cracks and potholes from dashcam/drone video, deduplicates detections.
</div>

---

## Team Information

| Name | Role | Contribution |
|------|------|-------------|
|  | Team Leader | Project coordination, model training, augmentation strategy |
|  | Data Engineer | Data collection, preprocessing, class merging, EDA |
|  | ML Engineer | Model evaluation, comparison, report writing |
|  | Developer | Backend API, frontend integration, deployment |

## Project Objectives

**Problem:** Road surface defects such as potholes and cracks pose a serious risk to vehicle safety and traffic flow. When vehicles are damaged by poorly maintained roads, the responsible municipality is liable for compensation — creating both a safety concern and a financial burden. Traditional manual inspections are slow, costly, and cannot cover an entire city effectively.

**Solution:** SABIQ automates road inspection using AI. Upload dashcam/drone video → detect defects → classify severity → store  → prioritize repairs.

**Vision 2030 Alignment:**
- **Smart Cities:** Riyadh ranked 24th globally in IMD Smart Cities Index 2026
- **Quality of Life Program:** Better roads = better daily life for millions
- **Year of AI 2026:** Practical AI application in municipal services

## Dataset

**Source:** [RDD2022](https://www.kaggle.com/datasets/aliabdelmenam/rdd-2022) 

- 47,420 images from 6 countries, 55,000+ damage annotations
- Split: Train 26,869 / Val 5,758 / Test 5,758
- Merged 4 classes → 3: **crack**, **other corruption**, **pothole**
- Augmented 7,788 pothole images (Albumentations) to fix class imbalance
- Final training set: 34,657 images

## Methodology

**1. Preprocessing:** Class merging (5→3), data cleaning, offline augmentation for potholes

**2. Model:** YOLO26m (21.7M params, 74.7 GFLOPs) — latest YOLO with C3k2 blocks and C2PSA attention

**3. Training:** 3 iterative versions on A100 GPU 

**4. Video Deduplication:** ByteTrack (ECCV 2022) assigns unique ID per defect across frames. Same defect in 30 frames → stored once.

## Implementation

**Stack:** Ultralytics YOLO · ByteTrack · FastAPI · HuggingFace Spaces · Loveable (React) · Supabase

**Challenges:**

| Challenge | Solution |
|-----------|----------|
| Potholes only 10% of data | Albumentations augmentation (+7,788 images) |
| Same defect repeated 30x in video | ByteTrack tracking — 1 ID per defect |
| Manual dedup was complex (50 lines) | ByteTrack replaced it (~10 lines) |

## Results

### Overall Performance

| Metric | V1 (YOLOv8m) | V2 (YOLO26m) | V3 (YOLO26m) 
|--------|-------------|-------------|--------------
| mAP50 | 0.636 | 0.621 | **0.636** | 
| mAP50-95 | 0.351 | 0.345 | **0.349** |
| Precision | 0.658 | 0.717 | 0.687 | 
| Recall | 0.605 | 0.558 | **0.585** |

### Per-Class Performance (V3 — Final Model)

| Class | Images | Precision | Recall | mAP50 | mAP50-95 |
|-------|--------|-----------|--------|-------|----------|
| Crack | 3,266 | 0.714 | 0.520 | 0.605 | 0.321 |
| Other | 1,093 | 0.714 | 0.745 | 0.792 | 0.493 |
| Pothole | 544 | 0.635 | 0.491 | 0.512 | 0.233 |
| **All** | **5,758** | **0.687** | **0.585** | **0.636** | **0.349** |


### Video Deduplication Results

| Metric | Without Tracking | With ByteTrack |
|--------|-----------------|----------------|
| Raw detections | 938 | — |
| Unique defects returned | 938 (all duplicates) | **86** |
| Reduction | — | **91%** |
| Cracks (unique) | 734 repeated | Deduplicated |
| Potholes (unique) | 204 repeated | Deduplicated |

## How to Run the Project

### Backend

```bash
git clone https://huggingface.co/spaces/Rahaf2001/sabiq-api
cd sabiq-api
pip install fastapi uvicorn ultralytics opencv-python-headless python-multipart lap
uvicorn main:app --reload --port 8000
# Open http://127.0.0.1:8000/docs to test
```
