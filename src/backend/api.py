#This should be the mainhub of our back end system 
#Dealing with requests, dealing with our "middle-people" within the application

from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from backend.sorting_rules import get_bin
from backend.classifier import classify_image


app = FastAPI()

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

#Don't think I need this anymore

#the lastest result should be the one shown to the front end, may cause issues if thrown incorrectly
latest_result: FrontendResult | None = None

#this should be changing with our two start and stop buttons
is_running = False

#just a health check thingy
@app.get("/")
def read_root():
    return {"message": "GarbageSort backend is running"}

#Below is where the two buttons lie 
@app.post("/start")
def start():
    global is_running
    is_running = True
    return {"running": True}

# hardware: stop button
@app.post("/stop")
def stop():
    global is_running
    is_running = False
    return {"running": False}

#when we need to classify the files
@app.post("/classify")
def classify_item(data: Classification):

    # Get the category predicted by the AI
    category = data.category

    # Get the AI confidence
    confidence = data.confidence

    # Determine which bin to use
    recommended_bin = get_bin(confidence, category)

    # Return the result
    return {
        "category": category,
        "confidence": confidence,
        "recommended_bin": recommended_bin
    }

# receives an image, returns what it is and which bin it goes in
@app.post("/classify", response_model=Classification)
async def classify_item(image: UploadFile = File(...)):
    global latest_result

    # make sure we actually got an image
    if not (image.content_type or "").startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    image_bytes = await image.read()

    # ask the AI what it thinks
    category, confidence = classify_image(image_bytes)

    # determine which bin to use
    recommended_bin = get_bin(confidence, category)

    latest_result = Classification(
        category=category,
        confidence=confidence,
        recommended_bin=recommended_bin,
    )
    return latest_result

# most recent result
@app.get("/latest", response_model=Classification)
def get_latest():
    if latest_result is None:
        raise HTTPException(status_code=404, detail="No item classified yet")
    return latest_result
 