import cv2
import time

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from fastapi.responses import StreamingResponse


from src.hardware.camera import Webcam




router = APIRouter(prefix="/camera", tags=["Camera"])

# One shared camera instance
camera = Webcam(camera_index=0)


@router.post("/freeze")
def freeze_camera():
    """Freeze camera and return captured image."""

    try:
        frame = camera.freeze()

        success, encoded_image = cv2.imencode(".jpg", frame)

        if not success:
            raise HTTPException(
                status_code=500,
                detail="Could not encode image"
            )

        return Response(
            content=encoded_image.tobytes(),
            media_type="image/jpeg"
        )

    except RuntimeError as error:
        raise HTTPException(status_code=503, detail=str(error))


@router.post("/unfreeze")
def unfreeze_camera():
    """Resume live camera."""

    camera.unfreeze()

    return {
        "status": "success",
        "frozen": False
    }


@router.get("/frame")
def get_camera_frame():
    """Get current camera image."""

    frame = camera.get_frame()

    if frame is None:
        raise HTTPException(
            status_code=503,
            detail="No camera frame available"
        )

    success, encoded_image = cv2.imencode(".jpg", frame)

    if not success:
        raise HTTPException(
            status_code=500,
            detail="Could not encode image"
        )

    return Response(
        content=encoded_image.tobytes(),
        media_type="image/jpeg"
    )


@router.get("/status")
def get_camera_status():
    """Check camera status."""

    return camera.get_status()


def generate_frames():
    """Continuously stream JPEG frames from the camera."""

    while True:
        frame = camera.get_frame()

        if frame is None:
            time.sleep(0.01)
            continue

        success, encoded_image = cv2.imencode(".jpg", frame)

        if not success:
            continue

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n"
            + encoded_image.tobytes()
            + b"\r\n"
        )


@router.get("/stream")
def stream_camera():
    """Stream live webcam footage."""

    return StreamingResponse(
        generate_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )