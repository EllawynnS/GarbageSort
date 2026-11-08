#The logic of classifying what an AI is, right now it is currently having no logic, so just going to put random stuff here
import random

from pydantic import BaseModel

#these are just the random catergories 
CATEGORIES = ["food_scraps", "recyclable_container", "paper", "garbage"]

#the AI result is here 
class AIResult(BaseModel):
    category: str
    confidence: float 


#just it randomly picking a category for now so that it can run 
def classify_image(image_bytes: bytes) -> AIResult:
    ##AI LOGIC GOES IN HERE adsgjghsdll;ag
     return AIResult(
        category=random.choice(CATEGORIES),
        confidence=round(random.uniform(0.3, 0.99), 2),
    )