#!/bin/bash
       # -v $(pwd):/workspace \
       #-v /tmp/.X11-unix:/tmp/.X11-unix \
       # -e DISPLAY=:1 

REPO_DIR=$(dirname $(dirname $(realpath $0)))

cd $REPO_DIR

VERSION=$(grep -oP "(?<=    version=')[^']*" setup.py)

docker run -it \
       --rm \
       --network=host \
       --gpus '"device=0"' \
       -v "$(pwd)"/data/examples:/home/user/easymocap/EasyMocap/data/examples \
       -v "$(pwd)":/home/user/easymocap/EasyMocap \
       eradorta/easymocap:$VERSION \
       /bin/bash


# docker run -it --rm --gpus '"device=0"' -v "$(pwd)"/data/examples:/openpose/examples/easy cwaffles/openpose