FROM python:3.12-slim

WORKDIR /app

RUN apt update -y && \
    apt install -y curl && \
    rm -rf /var/lib/apt/lists/*

# RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
RUN python -m pip install --upgrade pip

COPY requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir

COPY . .

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]