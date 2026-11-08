#The logic of classifying what an AI is, right now it is currently having no logic, so just going to put random stuff here
import io
import random

from PIL import Image, UnidentifiedImageError
from pydantic import BaseModel
import torch

from vision.classifier import _load_model, preprocess_image
#these are just the random catergories 
CATEGORIES = ["food_scraps", "recyclable_container", "paper", "garbage"]

LABEL_TO_CATEGORY = {
    "biological": "food_scraps",
    "paper": "paper",
    "cardboard": "paper",
    "plastic": "recyclable_container",
    "metal": "recyclable_container",
    "green-glass": "recyclable_container",
    "white-glass": "recyclable_container",
    "brown-glass": "recyclable_container",
    "brown-grass": "recyclable_container",   
    "battery": "garbage",
    "clothes": "garbage",
    "shoes": "garbage",
    "trash": "garbage",
}

#the AI result is here 
class AIResult(BaseModel):
    category: str
    confidence: float 

def label_to_category(label: str) -> str:
    cleaned = label.strip().lower().replace("_", "-").replace(" ", "-")
    return LABEL_TO_CATEGORY.get(cleaned, "garbage")

def warm_up():
    _load_model()

def classify_image(image_bytes: bytes) -> AIResult:

    # bytes -> picture
    try:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    except (UnidentifiedImageError, OSError) as error:
        raise ValueError("Could not read the image") from error

    # run the model
    processor, model, device = _load_model()
    inputs = preprocess_image(image, processor)
    inputs = {name: tensor.to(device) for name, tensor in inputs.items()}

    with torch.inference_mode():
        logits = model(**inputs).logits
        probabilities = torch.softmax(logits, dim=-1)[0]

    # add up the probability of every model label that belongs to each of our categories
    scores = {category: 0.0 for category in CATEGORIES}
    for index, probability in enumerate(probabilities.tolist()):
        label = model.config.id2label[index]
        scores[label_to_category(label)] += probability

    best = max(scores, key=scores.get)

    # debug line: shows what the model saw and what we turned it into
    top_index = int(probabilities.argmax())
    print(
        f"Model sees: {model.config.id2label[top_index]} ({probabilities[top_index]:.0%}) "
        f"-> {best} ({scores[best]:.0%})"
    )

    return AIResult(category=best, confidence=min(scores[best], 1.0))


#just it randomly picking a category for now so that it can run 
def classify_image(image_bytes: bytes) -> AIResult:
    ##AI LOGIC GOES IN HERE adsgjghsdll;ag
     return AIResult(
        category=random.choice(CATEGORIES),
        confidence=round(random.uniform(0.3, 0.99), 2),
    )