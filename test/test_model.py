import sys
from pathlib import Path

# make the project root importable, since this file lives in test/
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.vision.classifier import classify_waste  # change "classifier" to your module's filename

IMAGES = "test/images/trashcan.jpg"

if __name__ == "__main__":
    result = classify_waste(IMAGES)
    print(result)