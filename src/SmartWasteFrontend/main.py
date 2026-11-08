import sys
import threading
import time
from pathlib import Path

import requests
from PySide6.QtCore import QObject, Property, Signal, Slot, QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

API = "http://127.0.0.1:8000"   # if the API runs on another laptop, use its IP here

# how the API's names are shown on screen
CATEGORY_NAMES = {
    "food_scraps": "Food scraps",
    "recyclable_container": "Recyclable container",
    "paper": "Paper",
    "garbage": "Garbage",
}
BIN_NAMES = {
    "compost_bin": "Compost",
    "recycling_bin": "Recycling",
    "paper_bin": "Paper",
    "garbage_bin": "Garbage",
}


class AppController(QObject):
    statusChanged = Signal(str)
    resultChanged = Signal(str, str, float)    # item, bin, confidence

    def __init__(self):
        super().__init__()
        self._last_result = None

        threading.Thread(target=self._poll_latest, daemon=True).start()

    @Property(str, constant=True)
    def apiBase(self):
        return API

    @Slot()
    def pause(self):
        # freeze the camera first so the picture stops on the item, then stop processing
        threading.Thread(
            target=self._call,
            args=(["/camera/freeze", "/stop"], "Processing paused"),
            daemon=True,
        ).start()

    @Slot()
    def resume(self):
        # restart processing, then let the live camera feed continue
        threading.Thread(
            target=self._call,
            args=(["/start", "/camera/unfreeze"], "System ready"),
            daemon=True,
        ).start()

    def _call(self, paths, ok_status):
        """POST to each API path in order. Report the first one that fails."""
        for path in paths:
            try:
                response = requests.post(f"{API}{path}", timeout=5)
                print(f"[frontend] POST {path} -> {response.status_code}")
                response.raise_for_status()
            except requests.HTTPError as error:
                if path.startswith("/camera"):
                    self.statusChanged.emit("Camera not available")
                else:
                    self.statusChanged.emit(f"API error: {error.response.status_code}")
                return
            except requests.RequestException as error:
                print(f"[frontend] POST {path} failed: {error}")
                self.statusChanged.emit("Can't reach the API")
                return
        self.statusChanged.emit(ok_status)

    def _poll_latest(self):
        while True:
            try:
                response = requests.get(f"{API}/latest", timeout=3)
                if response.status_code == 200:
                    data = response.json()
                    result = (data["category"], data["recommended_bin"], data["confidence"])

                    if result != self._last_result:
                        self._last_result = result
                        self.resultChanged.emit(
                            CATEGORY_NAMES.get(data["category"], data["category"]),
                            BIN_NAMES.get(data["recommended_bin"], data["recommended_bin"]),
                            data["confidence"],
                        )
            except requests.RequestException:
                pass

            time.sleep(1)


app = QGuiApplication(sys.argv)
app.setOrganizationName("SmartWaste")
app.setApplicationName("SmartWaste")
engine = QQmlApplicationEngine()

controller = AppController()

engine.rootContext().setContextProperty(
    "backend", controller
)

QML_FILE = Path(__file__).resolve().parent / "SmartWasteFrontend" / "Main.qml"

engine.load(QUrl.fromLocalFile(str(QML_FILE)))

if not engine.rootObjects():
    sys.exit(-1)

sys.exit(app.exec())