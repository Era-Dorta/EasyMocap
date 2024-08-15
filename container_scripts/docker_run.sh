#!/bin/bash
if [ $# -ne 1 ]; then
    echo "Must provide the path to the data folder as argument"
    exit 1
fi

REPO_DIR=$(dirname $(dirname $(realpath $0)))

cd $REPO_DIR

VERSION=$(grep -oP "(?<=    version=')[^']*" setup.py)

DATA_PATH=$(readlink -f $1)

# Run an OpenPose server in the background for the keypoint detection
docker run \
    --rm \
    --network=host \
    --gpus all \
    -v ${DATA_PATH}:/home/user/easymocap/EasyMocap/data/examples/_data \
    eradorta/openpose:1.7.0 &

# Run the EasyMocap container which will communicate with the OpenPose server
docker run \
       --rm \
       --network=host \
       --gpus all \
       -v ${DATA_PATH}:/home/user/easymocap/EasyMocap/data/examples/_data \
       eradorta/easymocap:$VERSION
       &

wait

# Run in dev mode, including X11 flags for rendering and GUI stuff
# docker run \
#        -it \
#        --rm \
#        --network=host \
#        --gpus all \
#        -v "$(pwd)":/home/user/easymocap/EasyMocap \
#        -v /tmp/.X11-unix:/tmp/.X11-unix \
#        -e DISPLAY=:1 \
#        -v ${DATA_PATH}:/home/user/easymocap/EasyMocap/data/examples/_data \
#        eradorta/easymocap:$VERSION \
#        bash

