# Run the containers with the following flags
# --nv to get access to the nvidia GPUs in the host system
# --containall to not mount any directory from the host system by default
# --bind mount the data directorie in the container
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