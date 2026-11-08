#This should be the mainhub of our back end system 
#Dealing with requests, dealing with our "middle-people" within the application

from fastapi import FastAPI
from pydantic import BaseModel
from backend.sorting_rules import get_bin



app = FastAPI()

#so this is how the pydantic files work to convert it to python types and such
#we are carrying over the categories and confidence
#images? 
class Classification(BaseModel):
    category: str
    confidence: float

#get this when you open up the api
@app.get("/")
def read_root():
    return {"message": "GarbageSort backend is running"}

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