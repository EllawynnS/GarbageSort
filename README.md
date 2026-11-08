
# GarbageSort

GarbageSort is a Hackcamp 2026 project exploring an AI-assisted waste-sorting system. The prototype uses a webcam to capture an item, a Python backend to process the image and recommend a waste bin, and a desktop interface to display the result.

The project combines computer vision, software development, and embedded hardware. The Arduino integration and physical sorting mechanism are still under development.

## 1. Current Prototype

| Component | Technology | Status |
|---|---|---|
| Desktop frontend | PySide6 + Qt Quick (QML) | Implemented |
| Backend API | FastAPI + Uvicorn | Implemented |
| Camera | Logitech USB Webcam + OpenCV | Implemented |
| Image capture | OpenCV | Implemented |
| AI model | PyTorch + Hugging Face ViT | Model implemented, backend integration pending |
| Image processing | Pillow | Implemented in model code |
| Sorting rules | Python | Implemented |
| Database | SQLite | Implemented |
| Microcontroller | Arduino | Planned |
| Physical sorting mechanism | LEDs / actuators / bins | In development |

## 2. How the Application Works

1. The webcam continuously captures images in the background.
2. The frontend displays the live camera feed.
3. The user selects **Pause and Analyze** to capture an image.
4. The frontend sends a request to the FastAPI backend.
5. The backend freezes the current camera frame and processes the image.
6. The classification function returns a waste category and confidence score.
7. Sorting rules map the category to a recommended bin.
8. The classification result and captured image are stored in SQLite.
9. The frontend retrieves and displays the result.
10. The user can resume the camera feed.

**Current AI limitation:** The active classifier in `src/backend/classifier.py` currently returns placeholder random predictions. The separate ViT implementation in `src/vision/classifier.py` has not yet been connected to the active backend classification pipeline.

The backend also returns an LED index for each recommended bin. Physical LED control through the Arduino has not yet been implemented.

## 3. Repository Structure

```text
GarbageSort/
├── README.md
├── SYSTEM_ARCHITECTURE.md
├── requirements.txt
├── requirements-backend.txt
├── pyproject.toml
├── .python-version
├── main.py
│
├── config/
│
├── src/
│   ├── SmartWasteFrontend/
│   │   ├── main.py
│   │   ├── requirements.txt
│   │   ├── SmartWasteFrontend/
│   │   │   └── Main.qml
│   │   ├── badges/
│   │   └── recyclableContainersGuide.png
│   │
│   ├── backend/
│   │   ├── __init__.py
│   │   ├── api.py
│   │   ├── classifier.py
│   │   ├── db.py
│   │   ├── sorting_rules.py
│   │   └── system_manager.py
│   │
│   ├── hardware/
│   │   ├── __init__.py
│   │   ├── camera.py
│   │   ├── led.py
│   │   └── api/
│   │       └── camera_routes.py
│   │
│   ├── vision/
│   │   ├── classifier.py
│   │   ├── preprocessing.py
│   │   └── requirements.txt
│   │
│   └── garbagesort/
│
├── firmware/
│   └── arduino/
│       └── arduino.ino
│
└── test/
    ├── __init__.py
    └── images/
```

## 4. Requirements

- Python 3.13
- USB webcam supported by OpenCV
- Internet connection for downloading the Hugging Face model
- macOS, Windows, or Linux

### Python Dependencies

**Backend:**
- `uvicorn`
- `fastapi`
- `pillow`
- `torch`
- `huggingface_hub`
- `opencv-python`
- `python-multipart`
- `transformers`
- `safetensors`

**Frontend:**
- `PySide6`
- `requests`

## 5. Getting Started

The project uses Python 3.13 and a local virtual environment. The following commands are for macOS with Homebrew Python.

### Step 1. Create the virtual environment

Run these commands from the repository root:

```bash
rm -rf .venv

/opt/homebrew/opt/python@3.13/bin/python3.13 -m venv .venv

source .venv/bin/activate
```

### Step 2. Install backend dependencies

```bash
python -m pip install --upgrade pip

pip install uvicorn
pip install fastapi
pip install pillow
pip install torch
pip install huggingface_hub
pip install opencv-python
pip install python-multipart
pip install transformers
pip install safetensors
```

### Step 3. Run the backend

**Terminal 1: Backend**

From the repository root, activate the virtual environment if it is not already active.

```bash
source .venv/bin/activate

cd src

uvicorn backend.api:app --host 0.0.0.0 --port 8000
```

The backend runs at:

```text
http://127.0.0.1:8000
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

Keep this terminal running.

### Step 4. Install frontend dependencies

Open a second terminal.

Navigate to the repository root and activate the same virtual environment.

```bash
cd /path/to/GarbageSort

source .venv/bin/activate

pip install PySide6
pip install requests
```

### Step 5. Run the frontend

**Terminal 2: Frontend**

```bash
cd src/SmartWasteFrontend

python main.py
```

The PySide6 application will launch and communicate with the backend through HTTP requests.

**Important:** Both terminals must use the same `.venv` environment. You do not need to create a second virtual environment.

## 6. Camera Setup

The Logitech webcam connects directly to the computer through USB.

OpenCV is used to access the camera and retrieve image frames.

Current configuration:

- Camera interface: USB / UVC
- Python library: OpenCV (`cv2`)
- Default camera index: `0`
- Requested resolution: 1280 × 720

If the webcam is not detected, check the camera index in:

```text
src/hardware/api/camera_routes.py
```

The camera should be connected before starting the backend.

## 7. API Endpoints

The frontend communicates with the backend through HTTP requests.

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Backend health check |
| POST | `/start` | Enables scanning |
| POST | `/stop` | Disables scanning |
| POST | `/scan` | Captures and classifies the current frame |
| POST | `/classify` | Classifies an uploaded image |
| GET | `/latest` | Retrieves the latest classification |
| GET | `/camera/frame` | Retrieves the current camera frame |
| POST | `/camera/freeze` | Freezes the current camera frame |
| POST | `/camera/unfreeze` | Resumes camera capture |
| GET | `/camera/status` | Returns camera status |
| GET | `/camera/stream` | Streams camera frames |

See `src/backend/api.md` for additional API details.

## 8. Waste Categories

The current sorting rules map four application categories to recommended bins.

| Category | Recommended Bin | LED Index |
|---|---|---|
| `food_scraps` | Compost | 0 |
| `recyclable_container` | Recycling | 1 |
| `paper` | Paper | 2 |
| `garbage` | Garbage | 3 |

Predictions with confidence below `0.20` are currently routed to the garbage bin.

These are prototype rules and should be validated against the waste-sorting requirements of the target community.

## 9. Development Guidelines

- Hardware-related code belongs in `src/hardware/`.
- API endpoints and application coordination belong in `src/backend/`.
- Image classification and model inference belong in `src/vision/`.
- Frontend interface code belongs in `src/SmartWasteFrontend/`.
- Arduino firmware belongs in `firmware/arduino/`.
- Test images belong in `test/images/`.
- Keep API response formats and category names consistent between frontend and backend.
- Test individual modules before integrating them.
- Do not commit virtual environments, credentials, or large model files.

## 10. Current Development Tasks

| Task | Status |
|---|---|
| Webcam integration | Implemented |
| Live camera display | Implemented |
| Image capture and freeze | Implemented |
| FastAPI backend | Implemented |
| PySide6 frontend | Implemented |
| SQLite result storage | Implemented |
| Sorting category mapping | Implemented |
| Connect ViT model to backend classifier | Pending |
| Arduino serial communication | Pending |
| Physical LED control | Pending |
| Physical sorting mechanism | In development |

For more information about the software modules, hardware interfaces, and system workflow, see [SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md).
