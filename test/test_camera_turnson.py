import cv2


class Webcam:
    def __init__(self, camera_index=0):
        self.camera_index = camera_index
        self.camera = None

    def start(self):
        """Connect to the webcam."""
        self.camera = cv2.VideoCapture(self.camera_index)

        if not self.camera.isOpened():
            raise RuntimeError("Could not connect to webcam")

        # Set camera resolution
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        print("Webcam connected!")

    def read(self):
        """Capture one frame from the webcam."""
        if self.camera is None:
            return None

        success, frame = self.camera.read()

        if not success:
            return None

        return frame

    def stop(self):
        """Release webcam resources."""
        if self.camera is not None:
            self.camera.release()
            self.camera = None

        cv2.destroyAllWindows()


if __name__ == "__main__":
    webcam = Webcam(camera_index=0)

    try:
        webcam.start()

        while True:
            frame = webcam.read()

            if frame is None:
                print("Failed to capture frame")
                break

            cv2.imshow("Logitech Webcam", frame)

            # Press Q to quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        webcam.stop()