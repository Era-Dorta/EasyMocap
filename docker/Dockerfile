# Matching pytorch version
# FROM pytorch/pytorch:1.9.1-cuda11.1-cudnn8-devel

# Matching cuda version
# FROM pytorch/pytorch:1.13.1-cuda11.6-cudnn8-devel

# Latest version
FROM pytorch/pytorch:2.2.0-cuda12.1-cudnn8-devel

COPY requirements.txt .

ENV DEBIAN_FRONTEND=noninteractive

RUN apt update && \
    apt install -y git libgl1 libglib2.0-0 libsm6 libxrender1 libxext6 unzip wget && \
    rm -rf /var/lib/apt/lists/*

RUN python -m pip install -r requirements.txt && \
    pip install spconv-cu116 && \
    pip cache purge

