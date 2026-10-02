# RakshakAI – Project Folder Structure

## 1. Project Overview

RakshakAI is an AI-based object detection and tracking project organized into separate folders for datasets, source code, model weights, tracker configurations, outputs, testing files, and the Python environment.

This README explains the complete project folder structure and briefly describes the purpose of each important folder and file.

---

## 2. Complete Project Structure

```text
RakshakAI/
│
├── dataset/
│   ├── images/
│   ├── labels/
│   ├── raw/
│   ├── raw_labels/
│   └── data.yaml
│
├── images/
│
├── kaggle_dataset/
│
├── models/
│
├── outputs/
│   ├── annotation_check/
│   └── dataset_check/
│
├── runs/
│   ├── detect/
│   ├── rakshakai_test/
│   ├── rakshakai_test_predictions/
│   ├── rakshakai_train/
│   └── rakshakai_video/
│
├── src/
│   ├── analyze_classes.py
│   ├── auto_annotate.py
│   ├── detect_image.py
│   ├── detect_video.py
│   ├── evaluate_test.py
│   ├── prepare_final_dataset.py
│   ├── test_detection.py
│   ├── test_detection_stability.py
│   ├── test_yolo.py
│   ├── track_test.py
│   ├── train.py
│   ├── validate_dataset.py
│   ├── validate_final_dataset.py
│   ├── visualize_annotations.py
│   ├── visualize_final_dataset.py
│   └── webcam.py
│
├── trackers/
│   ├── bytetrack_rakshakai.yaml
│   └── ocsort_rakshakai.yaml
│
├── venv/
│
├── videos/
│
├── weights/
│
└── yolo26n.pt
```

---

# 3. Folder-by-Folder Explanation

## `dataset/`

This is the main dataset directory used for the YOLO-based object detection pipeline.

### `dataset/images/`

Contains image files used for training, validation, or testing of the object detection model.

### `dataset/labels/`

Contains YOLO-format annotation files corresponding to the images.

Each label file contains information such as:

- Class ID
- Object center coordinates
- Bounding-box width
- Bounding-box height

### `dataset/raw/`

Contains the original/raw images before final dataset preparation and preprocessing.

### `dataset/raw_labels/`

Contains the original annotations associated with the raw dataset.

### `dataset/data.yaml`

YOLO dataset configuration file.

It defines information such as:

- Dataset paths
- Number of classes
- Class names
- Training/validation dataset locations

---

## `images/`

Contains additional image files used during development, testing, visualization, or experimentation.

---

## `kaggle_dataset/`

Contains the dataset obtained from Kaggle that was used as a source during dataset preparation.

---

## `models/`

Contains model-related files and resources generated or used during development.

This directory can be used to store trained models or other model artifacts separately from the main source code.

---

# `outputs/`

Contains generated outputs from dataset preparation, annotation checking, and validation processes.

### `outputs/annotation_check/`

Contains outputs used to verify whether annotations and bounding boxes are correctly associated with the images.

### `outputs/dataset_check/`

Contains results generated while checking and validating the dataset.

---

# `runs/`

Contains experiment and result folders generated during YOLO training, testing, detection, and video processing.

### `runs/detect/`

Contains YOLO detection-related results.

### `runs/rakshakai_test/`

Contains outputs generated during RakshakAI model testing.

### `runs/rakshakai_test_predictions/`

Contains prediction results generated while testing the model.

### `runs/rakshakai_train/`

Contains training-related results such as:

- Training outputs
- Model checkpoints
- Validation results
- Performance graphs
- Training metrics

### `runs/rakshakai_video/`

Contains results generated during video-based detection or tracking experiments.

---

# `src/`

This is the main source-code directory of RakshakAI.

It contains the Python scripts responsible for dataset preparation, model training, validation, detection, visualization, webcam processing, and object tracking.

## `analyze_classes.py`

Analyzes the classes present in the dataset and helps inspect class distribution.

## `auto_annotate.py`

Used to automatically generate annotations for images.

## `detect_image.py`

Performs YOLO object detection on individual images.

## `detect_video.py`

Performs YOLO object detection on video input.

## `evaluate_test.py`

Evaluates the trained model on the test dataset and generates model-performance results.

## `prepare_final_dataset.py`

Prepares and organizes the final dataset into the required YOLO format.

## `test_detection.py`

Tests whether the trained YOLO model correctly detects the required objects.

## `test_detection_stability.py`

Used to check detection stability under different movement and camera conditions.

## `test_yolo.py`

Basic YOLO model testing script used to verify that the detection model is functioning correctly.

## `track_test.py`

Main real-time object tracking test script.

It uses the YOLO model with tracking enabled and performs:

- Person detection
- Vehicle detection
- Bounding-box generation
- Unique tracking ID assignment
- Continuous frame-by-frame tracking
- Real-time webcam visualization

The current tracking implementation uses:

```python
results = model.track(
    frame,
    persist=True,
    verbose=False
)
```

## `train.py`

Contains the code used to train the YOLO model on the prepared dataset.

## `validate_dataset.py`

Checks whether the dataset structure and annotations are valid.

## `validate_final_dataset.py`

Validates the final prepared dataset before model training and testing.

## `visualize_annotations.py`

Displays dataset annotations and bounding boxes to verify that the annotations are correct.

## `visualize_final_dataset.py`

Visualizes the final dataset and its annotations after dataset preparation.

## `webcam.py`

Handles webcam input and is used for real-time detection/testing through the camera.

---

# `trackers/`

Contains custom tracker configuration files used during multi-object tracking experiments.

## `bytetrack_rakshakai.yaml`

Custom ByteTrack configuration used for object-tracking experiments.

ByteTrack is a multi-object tracking algorithm that associates detections across consecutive video frames.

## `ocsort_rakshakai.yaml`

Custom OC-SORT configuration used for experimenting with another multi-object tracking approach.

OC-SORT is an observation-centric object tracking algorithm.

---

# `venv/`

Contains the Python virtual environment for the RakshakAI project.

The virtual environment keeps project-specific Python packages isolated from the system Python installation.

It contains dependencies such as:

- Python packages
- Ultralytics
- OpenCV
- PyTorch
- Other project dependencies

---

# `videos/`

Contains video files used for testing object detection and object tracking.

These videos can be used to evaluate how the system behaves with moving people and vehicles.

---

# `weights/`

Contains YOLO model weight files used by the project.

Model weight files contain the learned parameters required by the YOLO model for object detection.

---

# `yolo26n.pt`

This is the YOLO model weight file used by the RakshakAI detection and tracking pipeline.

The model is loaded in the Python code using:

```python
model = YOLO("weights/yolo26n.pt")
```

> Note: The exact location of a model file should match the path used in the Python script. If the model is stored inside `weights/`, the recommended path is `weights/yolo26n.pt`.

---

# 4. Overall Project Organization

The project can be understood through the following structure:

```text
                    RakshakAI
                        │
        ┌───────────────┼────────────────┐
        │               │                │
     Dataset         Source Code       Models
        │               │                │
    dataset/          src/            weights/
        │
        └───────────────┐
                        │
                  Model Training
                        │
                      runs/
                        │
                  Testing / Outputs
                        │
                 outputs/ + videos/
                        │
                  Object Tracking
                        │
                    trackers/
```

---

# 5. Role of Major Directories

| Directory | Purpose |
|---|---|
| `dataset/` | Stores the prepared and raw datasets |
| `images/` | Stores additional images used during development |
| `kaggle_dataset/` | Stores the source Kaggle dataset |
| `models/` | Stores model-related resources |
| `outputs/` | Stores generated validation and annotation outputs |
| `runs/` | Stores YOLO training, testing, and experiment results |
| `src/` | Contains the main Python source code |
| `trackers/` | Contains tracking algorithm configuration files |
| `venv/` | Contains the project's Python virtual environment |
| `videos/` | Stores videos used for detection/tracking tests |
| `weights/` | Stores YOLO model weight files |

---

# 6. Main Code Flow

The major components of the project are organized as:

```text
Raw Dataset
     │
     ▼
dataset/
     │
     ▼
Dataset Preparation & Validation
     │
     ├── prepare_final_dataset.py
     ├── validate_dataset.py
     └── validate_final_dataset.py
     │
     ▼
YOLO Model Training
     │
     └── train.py
     │
     ▼
Trained / Available Model
     │
     ▼
Detection
     │
     ├── detect_image.py
     └── detect_video.py
     │
     ▼
Object Tracking
     │
     └── track_test.py
     │
     ▼
Person / Vehicle + Tracking IDs
     │
     ▼
Testing & Results
     │
     ├── test_detection.py
     ├── test_detection_stability.py
     ├── evaluate_test.py
     ├── outputs/
     └── runs/
```

---

# 7. Summary

The RakshakAI project follows a modular folder structure where:

- `dataset/` handles dataset storage.
- `src/` contains the main implementation code.
- `weights/` contains model weights.
- `trackers/` contains tracking configurations.
- `runs/` stores experiment and model results.
- `outputs/` stores generated validation outputs.
- `videos/` stores testing videos.
- `venv/` provides an isolated Python environment.

This organization keeps the project's **data, source code, models, tracking configuration, experiments, and generated outputs** separated and easy to manage.
