FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-ttf-dev \
    libmagic-dev \
    ffmpeg \
    && curl https://sh.rustup.rs -sSf | sh -s -- -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

ENV PATH="/root/.cargo/bin:${PATH}"

WORKDIR /app

COPY ./bin/artc ./bin/artc
RUN chmod +x ./bin/artc

COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt

COPY . .

EXPOSE 9876

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9876"]
