from fastapi import FastAPI
from src.hardware.api.camera_routes import router, camera

app = FastAPI()

app.include_router(router)

@app.on_event("startup")
def startup():
    camera.start()


@app.on_event("shutdown")
def shutdown():
    camera.stop()
