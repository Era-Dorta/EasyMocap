# https://chingswy.github.io/easymocap-public-doc/install/install.html#20230630-update
# They recommend python 3.9 + cuda 11.6 + torch 1.12.0
# We are getting the closest pytorch version that is avaiable in docker hub for cuda 11.6
# ->             python 3.10 + cuda 11.6 + torch 1.13.1
ARG EASY_MOCAP_BASE_IMAGE_VERSION=0.2.1
FROM pytorch/pytorch:2.2.0-cuda12.1-cudnn8-runtime AS base

ENV DEBIAN_FRONTEND=noninteractive

# Default ffmpeg from conda doesn't have x264 support, replace with apt version of ffmpeg
RUN apt update && \
    apt install -y --no-install-recommends git ffmpeg && \
    rm /opt/conda/bin/ffmpeg && \
    ln -s /usr/bin/ffmpeg /opt/conda/bin/ffmpeg && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip3 install -r requirements.txt && \
    pip3 install spconv-cu116 pyrender && \
    pip3 cache purge

RUN useradd --create-home --shell /bin/bash --uid 1001 user
USER user
RUN mkdir -p /home/user/easymocap
WORKDIR /home/user/easymocap

FROM eradorta/easymocap:$EASY_MOCAP_BASE_IMAGE_VERSION-base AS runtime

RUN git clone https://github.com/Era-Dorta/EasyMocap.git --depth 1

USER root
RUN cd EasyMocap && \
    python3 -m pip install -r requirements.txt   && \
    python3 setup.py develop
USER user

WORKDIR /home/user/easymocap/EasyMocap

# For the git clone the EasyMocap folder had to be empty. Now that it happened, copy the data in there.
# Also tried puting the models in the previous stage and making hard links but docker just duplicated 
# the size of the image.
ARG EASY_MOCAP_MODELS
ADD --chown=user ${EASY_MOCAP_MODELS} ./data

CMD ["/home/user/easymocap/EasyMocap/container_scripts/entrypoint.sh"]

