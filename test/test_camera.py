import cv2
from pathlib import Path
from datetime import datetime

from src.hardware.camera import Webcam


# Create randomphotos directory in project root
PHOTO_DIR = Path("randomPhotos")
PHOTO_DIR.mkdir(parents=True, exist_ok=True)


def save_photo(frame):
    """Save a captured frame as a JPEG."""

    # Generate unique filename using timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    filename = PHOTO_DIR / f"photo_{timestamp}.jpg"

    success = cv2.imwrite(str(filename), frame)

    if success:
        print(f"Photo saved: {filename}")
    else:
        print("Failed to save photo!")


def main():
    camera = Webcam(camera_index=0)
    camera.start()

    print("Camera test started!")
    print("Press F to freeze and save photo")
    print("Press U to unfreeze")
    print("Press Q to quit")

    frozen = False

    try:
        while True:
            frame = camera.get_frame()

            if frame is None:
                continue

            display = frame.copy()

            if frozen:
                cv2.putText(
                    display,
                    "FROZEN",
                    (30, 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.2,
                    (0, 0, 255),
                    3
                )
            else:
                cv2.putText(
                    display,
                    "LIVE",
                    (30, 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.2,
                    (0, 255, 0),
                    3
                )

            cv2.imshow("GarbageSort Camera Test", display)

            key = cv2.waitKey(1) & 0xFF

            if key == ord('f') and not frozen:
                captured_frame = camera.freeze()

                save_photo(captured_frame)

                frozen = True
                print("Camera frozen!")

            elif key == ord('u') and frozen:
                camera.unfreeze()
                frozen = False
                print("Camera unfrozen!")

            elif key == ord('q'):
                break

    finally:
        camera.stop()


if __name__ == "__main__":
    main()
