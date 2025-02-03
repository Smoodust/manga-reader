from PIL import Image
from manga_ocr import MangaOcr

from io import BytesIO
import functools
from typing import Annotated

from fastapi import FastAPI, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from backend.ocr import YOLOv11

import uuid

data = {}


@functools.cache
def init_ocr_model():
    return MangaOcr()


@functools.cache
def init_detection_model():
    return YOLOv11("detection.onnx", 0.3, 0.1)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_ocr_model()
    init_detection_model()
    yield


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def ocr_image(ids: str):
    global data

    image = data[ids]["image"]
    mocr = init_ocr_model()
    for box in data[ids]["bbox"]:
        crop_image = image.crop(
            (box["x"], box["y"], box["x"] + box["w"], box["y"] + box["h"])
        )
        text = mocr(crop_image)
        data[ids]["ocrs"].append(text)
        print(len(data[ids]["ocrs"]))


@app.post("/add")
async def add_image(file: Annotated[bytes, File()], background_tasks: BackgroundTasks):
    global data

    stream = BytesIO(file)
    image = Image.open(stream)
    ids = str(uuid.uuid4())
    boxes = init_detection_model()(image)
    data[ids] = {"image": image, "bbox": boxes, "ocrs": []}
    background_tasks.add_task(ocr_image, ids)
    return ids


@app.post("/detect/{ids}")
async def get_detection_image(ids: str):
    return data[ids]["bbox"]


@app.post("/ocr/{ids}/{index_text}")
async def get_ocr_image(ids: str, index_text: int):
    return data[ids]["ocrs"][index_text]
