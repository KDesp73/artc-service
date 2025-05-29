FROM debian:sid

RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-ttf-dev \
    ffmpeg \
    python3.12 \
    python3.12-venv \
    python3.12-dev \
    python3-pip \
    && curl https://sh.rustup.rs -sSf | sh -s -- -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.12 1

ENV PATH="/root/.cargo/bin:${PATH}"

WORKDIR /app

COPY ./bin/artc ./bin/artc
RUN chmod +x ./bin/artc

COPY requirements.txt .
RUN pip3 install --upgrade pip setuptools wheel --break-system-packages
RUN pip3 install -r requirements.txt --break-system-packages

COPY . .

EXPOSE 9876

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9876"]
