FROM pytorch/pytorch:2.2.0-cuda12.1-cudnn8-devel as base

COPY requirements.txt .

ENV DEBIAN_FRONTEND=noninteractive

# System dependencies, first line are for easy mocap, second line for openpose
RUN apt update && \
    apt install -y git libgl1 libglib2.0-0 libsm6 libxrender1 libxext6 unzip wget && \
    apt install -y libopencv-dev protobuf-compiler libgoogle-glog-dev libboost-all-dev libhdf5-dev libatlas-base-dev cmake && \
    rm -rf /var/lib/apt/lists/*

RUN python -m pip install -r requirements.txt && \
    pip install spconv-cu116 pyrender && \
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

RUN useradd --create-home --shell /bin/bash --uid 1001 user
USER user
RUN mkdir -p /home/user/easymocap
WORKDIR /home/user/easymocap

RUN git clone https://github.com/CMU-Perceptual-Computing-Lab/openpose.git --depth 1 && \
    cd openpose  && \
    git submodule update --init --recursive --remote && \
    mkdir build    

# Build openpose with python support, wide GPU architure support and without downloading models as many fail to download
RUN cd openpose/build && \
    cmake .. \
    -DBUILD_PYTHON=true \
    -DDOWNLOAD_HAND_MODEL=OFF -DDOWNLOAD_FACE_MODEL=OFF -DDOWNLOAD_BODY_25_MODEL=OFF \
    -DBUILD_EXAMPLES=false \
    -DCUDA_ARCH=Manual -DCUDA_ARCH_BIN="61 62 70 72 75 80 86 87 89 90" -DCUDA_ARCH_PTX="61" && \
    make -j`nproc`

FROM base as runtime

RUN git clone https://github.com/Era-Dorta/EasyMocap.git --depth 1

USER root
RUN cd EasyMocap && \
    python -m pip install -r requirements.txt   && \
    python setup.py develop

USER user