
import sys
from pathlib import Path

from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QObject, Signal, Slot


class AppController(QObject):
    statusChanged = Signal(str)

    def __init__(self):
        super().__init__()
        self._status = "System ready"

    @Slot()
    def pause(self):
        # Connect to FastAPI later
        self._status = "Processing paused"
        self.statusChanged.emit(self._status)

    @Slot()
    def resume(self):
        # Connect to FastAPI later
        self._status = "System ready"
        self.statusChanged.emit(self._status)


app = QGuiApplication(sys.argv)
engine = QQmlApplicationEngine()

controller = AppController()

engine.rootContext().setContextProperty(
    "backend", controller
)

qml_file = Path(__file__).parent / "SmartWasteFrontend\\Main.qml"
engine.load(str(qml_file))

if not engine.rootObjects():
    sys.exit(-1)

sys.exit(app.exec())
