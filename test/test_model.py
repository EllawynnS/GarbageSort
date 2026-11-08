import sys
from pathlib import Path

# make the project root importable, since this file lives in test/
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.vision.classifier import classify_waste, get_top_waste_prediction

# resolve relative to the project root so it works from any working directory
IMAGES = str(ROOT / "test" / "images" / "can.jpeg")

# Test 1: classify_waste function
if __name__ == "__main__":
    result = classify_waste(IMAGES)
    print(result)


# Test 2: get_top_waste_prediction function
if __name__ == "__main__":
    waste_type, confidence = get_top_waste_prediction(IMAGES)
    print("\n========================================")
    print(f"Type: {waste_type}")
    print(f"Confidence: {confidence}")
    print(type(waste_type), type(confidence))
    print("\n========================================")
