#!/bin/bash
REPO_DIR=$(dirname $(dirname $(realpath $0)))

cd $REPO_DIR

if [ $# -ne 1 ]; then
    echo "Must provide your netid as argument"
    exit 1
fi

########
# Copy the model data from staff umbrella to the local docker context, ideally we would just mount the folder
# but that is very slow. A better solution is to use hard links but that doesn't work with sshfs and with the
# underlying filesystem. So we copy all the data to the local context and then build the image
########

# Create a folder for the CaptureLab project in staff umbrella
CAPTURE_LAB_DIR=/tmp/staff_umbrella_capturelab
mkdir $CAPTURE_LAB_DIR

OPEN_POSE_MODELS_TMP=$CAPTURE_LAB_DIR/Openpose/models
EASY_MOCAP_MODELS_TMP=$CAPTURE_LAB_DIR/EasyMocap/data

# If not already available, mount it via sshfs
if [ ! -d "$OPEN_POSE_MODELS_TMP" ]; then
    sshfs -o ro $1@sftp.tudelft.nl:/staff-umbrella/CaptureLab $CAPTURE_LAB_DIR
fi

OPEN_POSE_MODELS_LOCAL=tmp_models/Openpose_models/models
EASY_MOCAP_MODELS_LOCAL=tmp_models/EasyMocap_models/data

if [ ! -d "$OPEN_POSE_MODELS_LOCAL" ]; then
    mkdir -p "$(dirname "$OPEN_POSE_MODELS_LOCAL")"
    cp --recursive $OPEN_POSE_MODELS_TMP "$(dirname "$OPEN_POSE_MODELS_LOCAL")"
fi

if [ ! -d "$EASY_MOCAP_MODELS_LOCAL" ]; then
    mkdir -p "$(dirname "$EASY_MOCAP_MODELS_LOCAL")"
    cp --recursive $EASY_MOCAP_MODELS_TMP "$(dirname "$EASY_MOCAP_MODELS_LOCAL")"
fi

docker build \
    --progress=plain \
    --target runtime \
    --build-arg OPEN_POSE_MODELS=$OPEN_POSE_MODELS_LOCAL \
    --build-arg EASY_MOCAP_MODELS=$EASY_MOCAP_MODELS_LOCAL \
    --tag local/easymocap:pytorch2.2.0-cuda12.1 \
    ${REPO_DIR}

# umount $CAPTURE_LAB_DIR