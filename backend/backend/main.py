from PIL import Image
from manga_ocr import MangaOcr
from ultralytics import YOLO

from io import BytesIO
import functools
from typing import Annotated

from fastapi import FastAPI, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

import uuid

data = {}


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
    results = init_detection_model()(image, iou=0.1)
    boxes = results[0].boxes
    boxes = [
        {
            "conf": conf,
            "x": box[0] - box[2] / 2,
            "y": box[1] - box[3] / 2,
            "w": box[2],
            "h": box[3],
        }
        for conf, box in zip(boxes.conf.tolist(), boxes.xywh.tolist())
    ]
    data[ids] = {"image": image, "bbox": boxes, "ocrs": []}
    background_tasks.add_task(ocr_image, ids)
    return ids


@app.post("/detect/{ids}")
async def get_detection_image(ids: str):
    return data[ids]["bbox"]


@app.post("/ocr/{ids}/{index_text}")
async def get_ocr_image(ids: str, index_text: int):
    return data[ids]["ocrs"][index_text]
