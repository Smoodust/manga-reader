from PIL import Image
from manga_ocr import MangaOcr

from io import BytesIO
import functools
from typing import Annotated

from fastapi import FastAPI, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from backend.ocr import YOLOv11
from transformers.utils.logging import set_verbosity_error

import uuid
import json

import valkey

@functools.cache
def init_ocr_model():
    return MangaOcr()


@functools.cache
def init_detection_model():
    return YOLOv11("detection.onnx", 0.3, 0.1)


@asynccontextmanager
async def lifespan(app: FastAPI):
    set_verbosity_error()
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


def ocr_image(ids: str, image: Image.Image):
    connection = valkey.Valkey(host="redis", port=6379)
    data = json.loads(connection.get(ids).decode("utf-8"))
    mocr = init_ocr_model()
    for box in data["bbox"]:
        crop_image = image.crop(
            (box["x"], box["y"], box["x"] + box["w"], box["y"] + box["h"])
        )
        text = mocr(crop_image)
        data["ocrs"].append(text)
        connection.set(ids, json.dumps(data))
    connection.close()


@app.post("/add")
async def add_image(file: Annotated[bytes, File()], background_tasks: BackgroundTasks):
    stream = BytesIO(file)
    image = Image.open(stream)
    ids = str(uuid.uuid4())
    boxes = init_detection_model()(image)
    data = {"bbox": boxes, "ocrs": []}

    connection = valkey.Valkey(host="redis", port=6379)
    connection.set(ids, json.dumps(data))
    connection.close()
    
    background_tasks.add_task(ocr_image, ids, image)
    return ids


@app.post("/detect/{ids}")
async def get_detection_image(ids: str):
    connection = valkey.Valkey(host="redis", port=6379)
    data = json.loads(connection.get(ids).decode("utf-8"))
    return data["bbox"]


@app.post("/ocr/{ids}/{index_text}")
async def get_ocr_image(ids: str, index_text: int):
    connection = valkey.Valkey(host="redis", port=6379)
    data = json.loads(connection.get(ids).decode("utf-8"))
    return data["ocrs"][index_text]
