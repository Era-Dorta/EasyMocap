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
    pip install spconv-cu116 pyrender && \
    cd /workspace/library/pymatch && \
    python3 setup.py develop && \
    pip cache purge

# Fix missing dri and wrong GCC versions with OpenGL
RUN ln -sn /usr/lib/x86_64-linux-gnu/dri /usr/lib/dri
ENV LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libstdc++.so.6

# Default ffmpeg from conda doesn't have x264 support, replace with apt version of ffmpeg
RUN apt update && \
    apt install -y ffmpeg && \
    rm -rf /var/lib/apt/lists/* && \
    rm /opt/conda/bin/ffmpeg && \
    ln -s /usr/bin/ffmpeg /opt/conda/bin/ffmpeg