FROM pytorch/pytorch:2.2.0-cuda12.1-cudnn8-devel

COPY requirements.txt .

ENV DEBIAN_FRONTEND=noninteractive

RUN apt update && \
    apt install -y git libgl1 libglib2.0-0 libsm6 libxrender1 libxext6 unzip wget && \
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

# Install OpenPose dependencies
RUN apt update && \
apt install -y libopencv-dev protobuf-compiler libgoogle-glog-dev libboost-all-dev libhdf5-dev libatlas-base-dev && \
rm -rf /var/lib/apt/lists/*

# Install OpenPose dependencies
RUN git clone https://github.com/CMU-Perceptual-Computing-Lab/openpose.git --depth 1 && \
    cd openpose  && \
    git submodule update --init --recursive --remote && \
    mkdir build    

RUN cd openpose/build && \
    cmake .. -DBUILD_PYTHON=true \
    -DDOWNLOAD_HAND_MODEL=OFF -DDOWNLOAD_FACE_MODEL=OFF -DDOWNLOAD_BODY_25_MODEL=OFF \
    -DCUDA_ARCH=Manual -DCUDA_ARCH_BIN="60 61 62 70 72 75 80 86 87 89 90" -DCUDA_ARCH_PTX="61" && \
    make -j`nproc`
