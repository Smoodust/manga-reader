from PIL import Image
from manga_ocr import MangaOcr
from io import BytesIO
import functools
from typing import Annotated

from fastapi import FastAPI, File, UploadFile
from contextlib import asynccontextmanager


@functools.cache
def init_ocr_model():
    return MangaOcr()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_ocr_model()
    yield


app = FastAPI(lifespan=lifespan)


@app.post("/ocr")
async def create_file(file: Annotated[bytes, File()]):
    stream = BytesIO(file)
    image = Image.open(stream)

    mocr = init_ocr_model()
    return mocr(image)
