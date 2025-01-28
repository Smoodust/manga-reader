from PIL import Image
from manga_ocr import MangaOcr
from ultralytics import YOLO

from io import BytesIO
import functools
from typing import Annotated

from fastapi import FastAPI, File, UploadFile
from contextlib import asynccontextmanager


@functools.cache
def init_ocr_model():
    return MangaOcr()


@functools.cache
def init_detection_model():
    return YOLO("detection.onnx", task="detect")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_ocr_model()
    init_detection_model()
    yield


app = FastAPI(lifespan=lifespan)


@app.post("/detect")
async def detect_image(file: Annotated[bytes, File()]):
    stream = BytesIO(file)
    image = Image.open(stream)
    results = init_detection_model()(image)
    boxes = results[0].boxes
    boxes = [
        {"conf": conf, "x": box[0], "y": box[1], "w": box[2], "h": box[3]}
        for conf, box in zip(boxes.conf.tolist(), boxes.xywh.tolist())
    ]
    return boxes


@app.post("/ocr")
async def ocr_image(file: Annotated[bytes, File()]):
    stream = BytesIO(file)
    image = Image.open(stream)

    mocr = init_ocr_model()
    return mocr(image)
