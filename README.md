## Overview

This repository contains the software and embedded firmware for our Hackcamp 2026 project.

The Hackcamp theme is:

> Identify a problem facing a community and build a solution that makes a meaningful difference.

The specific community problem, proposed solution, and project name will be documented here once the team has finalized them.

## System Overview

The current planned prototype uses:

- **Laptop / Desktop:** Runs the main Python application, computer vision, backend coordination, and user interface.
- **Logitech HD USB Webcam:** Captures images and video for computer vision using OpenCV.
- **Arduino:** Controls connected electronics and peripherals, communicating with the computer over USB serial.
- **Python:** Used for camera acquisition, image processing, AI inference, hardware communication, and system coordination.
- **Frontend:** To be determined. Streamlit is a candidate for a Python-based prototype.

> **Camera note:** The Logitech webcam connects over USB. 

## Repository Structure

```text
.
├── README.md
├── SYSTEM_ARCHITECTURE.md
├── requirements.txt
├── .gitignore
├── main.py
├── config/
├── src/
│   ├── hardware/
│   │   ├── camera.py
│   │   ├── arduino.py
│   │   └── led.py
│   ├── vision/
│   │   ├── preprocessing.py
│   │   └── classifier.py
│   ├── backend/
│   │   └── system_manager.py
│   └── frontend/
│       ├── app.py
│       └── components.py
├── firmware/
│   └── arduino/
│       └── arduino.ino
├── tests/
├── data/
│   ├── samples/
│   └── processed/
├── models/
└── docs/
```

## Getting Started

### 1. Clone the Repository

```bash

```

### 2. Create a Virtual Environment

macOS / Linux:

```bash

```

Windows:

```powershell

```

### 3. Install Dependencies

```bash

```

### 4. Connect Hardware

- Connect the Logitech webcam to the computer over USB.
- Connect the Arduino to the computer over USB.
- Identify the Arduino serial port.
- Ensure the Arduino firmware and Python serial settings use the same baud rate.

Common serial port examples:


### 5. Run the Application

The application entry point and run command will be added once the frontend and backend are implemented.

## Development Conventions

- Hardware-specific code belongs in `src/hardware/`.
- Image processing and model inference belong in `src/vision/`.
- Application logic and coordination belong in `src/backend/`.
- User-interface code belongs in `src/frontend/`.
- Arduino firmware belongs in `firmware/arduino/`.
- Add tests for individual modules and end-to-end behaviour.
- Avoid committing virtual environments, credentials, large datasets, or model weights without an agreed storage strategy.
- Document changes to shared interfaces and communication protocols.


## Documentation

- [System Architecture](SYSTEM_ARCHITECTURE.md): Hardware connections, software modules, data flow, and integration decisions.
- `docs/`: Additional design notes, wiring diagrams, testing procedures, and meeting decisions.

