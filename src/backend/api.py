#This should be the mainhub of our back end system 
#Dealing with requests, dealing with our "middle-people" within the application

import base64

from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from backend.sorting_rules import get_bin, get_led
from backend.classifier import classify_image
from hardware.api.camera_routes import router as camera_router, camera

from contextlib import asynccontextmanager 
import cv2 

@asynccontextmanager
async def lifespan(app):
    try:
        camera.start()
    except RuntimeError as error:
        print(f"WARNING: camera not started: {error}")   # the API still works without a webcam
    yield
    camera.stop()

app = FastAPI(lifespan=lifespan)

app.include_router(camera_router)

#this is for possible front end differences
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

#so this is how the pydantic files work to convert it to python types and such
#we are carrying over the categories and confidence
#images? 

#Okay this is now going to have to be cut up in three ways 

#this is what the hardware is going to need as a response when gathering back the requests
class HardwareResponse(BaseModel):
    recommended_bin: str
    led: int 

#what the front-ends needs to actually function
class FrontendResult(BaseModel):
    image: str        
    category: str
    confidence: float
    recommended_bin: str  



#the lastest result should be the one shown to the front end, may cause issues if thrown incorrectly


latest_result: FrontendResult | None = None

is_running = False


def process_photo(image_bytes: bytes, content_type: str) -> HardwareResponse:
    global latest_result

    ai_result = classify_image(image_bytes)

    recommended_bin = get_bin(ai_result.confidence, ai_result.category)
    led = get_led(recommended_bin)

    encoded = base64.b64encode(image_bytes).decode("utf-8")
    latest_result = FrontendResult(
        image=f"data:{content_type};base64,{encoded}",
        category=ai_result.category,
        confidence=ai_result.confidence,
        recommended_bin=recommended_bin,
    )

    return HardwareResponse(recommended_bin=recommended_bin, led=led)


# send a photo file (for testing, or hardware on another device)
@app.post("/classify", response_model=HardwareResponse)
async def classify_item(image: UploadFile = File(...)):

    if not is_running:
        raise HTTPException(status_code=409, detail="Not running. Press start first.")

    content_type = image.content_type or ""
    if not content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    image_bytes = await image.read()
    return process_photo(image_bytes, content_type)


# NEW: take a photo with the webcam, classify it, return the bin and LED
@app.post("/scan", response_model=HardwareResponse)
def scan():

    if not is_running:
        raise HTTPException(status_code=409, detail="Not running. Press start first.")

    # freeze the camera and grab the still
    try:
        frame = camera.freeze()
    except RuntimeError as error:
        raise HTTPException(status_code=503, detail=str(error))

    try:
        ok, buffer = cv2.imencode(".jpg", frame)
        if not ok:
            raise HTTPException(status_code=500, detail="Could not encode image")

        return process_photo(buffer.tobytes(), "image/jpeg")

    finally:
        camera.unfreeze()    # always resume live video


#just a health check thingy
@app.get("/")
def read_root():
    return {"message": "GarbageSort backend is running"}

#Below is where the two buttons lie 

#start button
#this should be the start button 
@app.post("/start")
def start():
    global is_running
    is_running = True
    return {"running": True}

#stop button 
@app.post("/stop")
def stop():
    global is_running
    is_running = False
    return {"running": False}


# most recent result, added check so that there isn't any errors

#Checking whether the result is there
@app.get("/latest", response_model=FrontendResult)
def get_latest():
    if latest_result is None:
        raise HTTPException(status_code=404, detail="No item classified yet")
    return latest_result
 