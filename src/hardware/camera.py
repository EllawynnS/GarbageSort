import cv2
import threading


import cv2
import threading


class Webcam:
    def __init__(self, camera_index=0):
        self.camera_index = camera_index
        self.camera = None

        self.latest_frame = None
        self.frozen_frame = None

        self.is_frozen = False
        self.is_running = False

        self.lock = threading.Lock()
        self.thread = None

    def start(self):
        """Connect to webcam and start capturing frames."""

        self.camera = cv2.VideoCapture(self.camera_index)

        if not self.camera.isOpened():
            raise RuntimeError("Could not connect to webcam")

        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        self.is_running = True

        self.thread = threading.Thread(
            target=self._capture_loop,
            daemon=True
        )
        self.thread.start()

        print("Webcam started!")

    def _capture_loop(self):
        """Continuously capture frames in the background."""

        while self.is_running:
            success, frame = self.camera.read()

            if success:
                with self.lock:
                    self.latest_frame = frame

    def freeze(self):
        """Capture and save the current frame."""

        with self.lock:
            if self.latest_frame is None:
                raise RuntimeError("No camera frame available")

            self.frozen_frame = self.latest_frame.copy()
            self.is_frozen = True

            return self.frozen_frame.copy()

    def unfreeze(self):
        """Resume displaying live camera frames."""

        with self.lock:
            self.frozen_frame = None
            self.is_frozen = False

    def get_frame(self):
        """Return frozen image or latest live frame."""

        with self.lock:
            if self.is_frozen:
                return self.frozen_frame.copy()

            if self.latest_frame is None:
                return None

            return self.latest_frame.copy()

    def get_status(self):
        """Return current camera status."""

        with self.lock:
            return {
                "running": self.is_running,
                "frozen": self.is_frozen
            }

    def stop(self):
        """Stop camera and release resources."""

        self.is_running = False

        if self.thread is not None:
            self.thread.join(timeout=2)

        if self.camera is not None:
            self.camera.release()
            self.camera = None

        cv2.destroyAllWindows()
        print("Webcam stopped!")
