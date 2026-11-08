# GarbageSort API

Backend that connects the hardware, the CV model, and the front end.

**Base URL:** `http://<laptop-ip>:8000`
Run with: `uvicorn backend.api:app --host 0.0.0.0 --port 8000`
Live interactive docs: `http://<laptop-ip>:8000/docs`

## Overview

```
Hardware  --photo, start, stop-->  API  --photo-->  CV model
Hardware  <--bin and LED---------  API  <--category, confidence--  CV model
Front end <--image, category, confidence--  API
```

The API only answers requests. Hardware and front end each ask, and the API replies.

## Fixed values

| Field | Allowed values |
|---|---|
| `category` | `food_scraps`, `recyclable_container`, `paper`, `garbage` |
| `recommended_bin` | `compost_bin`, `recycling_bin`, `paper_bin`, `garbage_bin` |
| `led` | `0`, `1`, `2`, `3` (left to right) |

LED positions:

| led | Bin | Category |
|---|---|---|
| 0 (leftmost, green) | compost_bin | food_scraps |
| 1 | recycling_bin | recyclable_container |
| 2 | paper_bin | paper |
| 3 | garbage_bin | garbage |

Items with confidence below 0.20, or with an unknown category, go to `garbage_bin` (led 3).

---

## Hardware endpoints

### POST /start
Start button pressed. No body.

Response:
```json
{
  "running": true
}
```

### POST /stop
Stop button pressed. No body.

Response:
```json
{
  "running": false
}
```

### POST /classify
Send a photo. Must be a file upload (multipart form data) with the field name `image`.
Only works after `/start` has been called.

The response is how the hardware finds out which bin the item goes in and which LED to light.

Response:
```json
{
  "recommended_bin": "paper_bin",
  "led": 2
}
```

| Field | Type | Notes |
|---|---|---|
| `recommended_bin` | string | One of `compost_bin`, `recycling_bin`, `paper_bin`, `garbage_bin` |
| `led` | integer | Which LED to light, `0` (leftmost) to `3` (rightmost). See the LED positions table above. |

---

## Front end endpoints

### GET /latest
Most recent classified item. Poll every second or so.

Response:
```json
{
  "image": "data:image/jpeg;base64,/9j/4AAQSkZJRg...",
  "category": "paper",
  "confidence": 0.87
}
```

| Field | Type | Notes |
|---|---|---|
| `image` | string | Data URL (`data:image/jpeg;base64,...`). Decode the part after the comma to get the raw image bytes. |
| `category` | string | One of the four categories above |
| `confidence` | number | 0.0 to 1.0 |

---

## CV model (internal)

Not an HTTP endpoint. It's a Python function in `backend/classifier.py`:

```python
classify_image(image_bytes: bytes) -> AIResult
```

It takes the photo's raw bytes and returns:
```json
{
  "category": "paper",
  "confidence": 0.87
}
```

`category` must be exactly one of the four categories. `confidence` must be between 0.0 and 1.0.

---

## Errors

All errors have the same shape:
```json
{
  "detail": "Not running. Press start first."
}
```

| Status | When |
|---|---|
| 400 | Uploaded file is not an image |
| 404 | `GET /latest` before anything has been classified |
| 409 | `POST /classify` before `/start` (or after `/stop`) |
| 422 | `POST /classify` with no `image` field |

Check the status code first, then read `detail` for a message.

---

## Typical flow

1. Hardware: `POST /start`
2. Hardware: `POST /classify` with a photo, receives `{"recommended_bin": "paper_bin", "led": 2}`, lights LED 2
3. Front end: `GET /latest`, gets the image, category, and confidence
4. Hardware: `POST /stop`