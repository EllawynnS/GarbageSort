import sys
import threading
import time
from pathlib import Path

import requests
from PySide6.QtCore import QObject, Property, Signal, Slot, QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

from stats import StatsTracker   # stats.py sits next to this file

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
    statsChanged = Signal(str)                 # JSON text, handled by applyStats() in Main.qml

    def __init__(self):
        super().__init__()
        self._last_result = None

        # keeps the counts and badges in stats.py / stats.json and pushes them to Main.qml
        self.tracker = StatsTracker(on_change=self.statsChanged.emit)

        threading.Thread(target=self._poll_latest, daemon=True).start()

    @Property(str, constant=True)
    def apiBase(self):
        return API

    # NEW: the "Reset progress" link in the Stats popup
    @Slot()
    def resetProgress(self):
        self.tracker.reset()

    # NEW: demo keys 7 / 8 / 9 in Main.qml set "days online" to 0 / 1 / 7
    @Slot(int)
    def setDemoDays(self, days):
        self.tracker.set_days(days)

    # CHANGED: "Pause and analyze" now freezes the picture AND scans it
    @Slot()
    def pause(self):
        threading.Thread(target=self._pause_and_analyze, daemon=True).start()

    # unchanged: "Resume feed"
    @Slot()
    def resume(self):
        # restart processing, then let the live camera feed continue
        threading.Thread(
            target=self._call,
            args=(["/start", "/camera/unfreeze"], "System ready"),
            daemon=True,
        ).start()

    # NEW: freeze on the item, scan it, show the result
    def _pause_and_analyze(self):
        try:
            # the screen has no Start button, so make sure the API is running
            requests.post(f"{API}/start", timeout=5)

            self.statusChanged.emit("Analyzing...")

            # keep_frozen=true makes the video stay frozen on the item after the scan
            response = requests.post(
                f"{API}/scan", params={"keep_frozen": "true"}, timeout=30
            )
            print(f"[frontend] POST /scan -> {response.status_code}")

            if response.status_code == 503:
                self.statusChanged.emit("Camera not available")
                return
            if response.status_code != 200:
                self.statusChanged.emit(f"API error: {response.status_code}")
                return

            # show the result straight away instead of waiting for the next poll
            result = self._check_latest(force=True)
            if result is not None:
                # a scan just finished: count it (updates stats.py and Main.qml)
                self.tracker.record_scan(BIN_NAMES.get(result[1], result[1]))
            self.statusChanged.emit("Processing paused")

        except requests.RequestException as error:
            print(f"[frontend] POST /scan failed: {error}")
            self.statusChanged.emit("Can't reach the API")

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

    # CHANGED: the /latest check moved into its own method so both the poller and the scan can use it
    def _check_latest(self, force=False):
        """Fetch /latest and update the screen if it changed (or if force is True).
        Returns (category, bin, confidence), or None if /latest could not be read."""
        try:
            response = requests.get(f"{API}/latest", timeout=3)
            if response.status_code != 200:
                return None
            data = response.json()
        except requests.RequestException:
            return None

        result = (data["category"], data["recommended_bin"], data["confidence"])
        if force or result != self._last_result:
            self._last_result = result
            self.resultChanged.emit(
                CATEGORY_NAMES.get(data["category"], data["category"]),
                BIN_NAMES.get(data["recommended_bin"], data["recommended_bin"]),
                data["confidence"],
            )
        return result

    def _poll_latest(self):
        while True:
            self._check_latest()
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

# push the saved stats once now that the QML is loaded, so the header badges show
# and the very first new badge pops its toast
controller.statsChanged.emit(controller.tracker.to_json())

sys.exit(app.exec())