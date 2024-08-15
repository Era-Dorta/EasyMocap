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

# Create a tmp folder where we will mount the CaptureLab project from the staff umbrella storage
CAPTURE_LAB_DIR=/tmp/staff_umbrella_capturelab
mkdir $CAPTURE_LAB_DIR

EASY_MOCAP_MODELS_TMP=$CAPTURE_LAB_DIR/EasyMocap/data

# Check if it is mounted and mount if via sshfs if it is not mounted
if [ ! -d "$EASY_MOCAP_MODELS_TMP" ]; then
    sshfs -o ro $1@sftp.tudelft.nl:/staff-umbrella/CaptureLab $CAPTURE_LAB_DIR
fi

EASY_MOCAP_MODELS_LOCAL=tmp_models/EasyMocap_models/data

# Copy the data to the local docker context
if [ ! -d "$EASY_MOCAP_MODELS_LOCAL" ]; then
    mkdir -p "$(dirname "$EASY_MOCAP_MODELS_LOCAL")"
    cp --recursive $EASY_MOCAP_MODELS_TMP "$(dirname "$EASY_MOCAP_MODELS_LOCAL")"
fi

VERSION=$(grep -oP "(?<=    version=')[^']*" setup.py)

docker build \
    --progress=plain \
    --target runtime \
    --build-arg EASY_MOCAP_MODELS=$EASY_MOCAP_MODELS_LOCAL \
    --tag eradorta/easymocap:$VERSION \
    ${REPO_DIR}

