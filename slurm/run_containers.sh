#!/bin/sh

# 3D keypoint extraction and visualisation using OpenPose and EasyMocap

# The OpenPose container waits for commands from the EasyMocap container

# Run the containers with the following flags
# --nv to get access to the nvidia GPUs in the host system
# --containall to not mount any directory from the host system by default
# --bind mount the data directory in the container
apptainer run \
    --nv \
    --containall \
    --bind "${DATA_DIRECTORY}"/Rec${RECORDING_NUMBER}_png:"${CONTAINER_DATA_DIRECTORY}" \
    $OPENPOSE_IMAGE &

apptainer run \
    --nv \
    --containall \
    --bind "${DATA_DIRECTORY}"/Rec${RECORDING_NUMBER}_png:"${CONTAINER_DATA_DIRECTORY}" \
    $EASYMOCAP_IMAGE  &

wait