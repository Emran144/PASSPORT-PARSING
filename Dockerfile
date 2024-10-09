# FROM ultralytics/ultralytics
FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    tesseract-ocr

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install transformers
RUN pip install tiktoken
RUN pip install verovio
RUN pip install 'accelerate>=0.26.0'
RUN pip install numpy==1.23.5
RUN pip install paddlepaddle paddleocr
RUN pip install pymupdf
RUN pip install mrz
RUN pip install sentencepiece

COPY . .

EXPOSE 5052

CMD ["python", "passport_app.py"]