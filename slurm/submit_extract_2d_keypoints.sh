#!/bin/sh
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=16G
#SBATCH --time=5:00
#SBATCH --qos=long
#SBATCH --gres=gpu
#SBATCH --exclude=gpu[01-12],gpu[14-29]
 
# Exclude the A40 GPUs, OpenPose cannot run in those.

# 3D keypoint extraction and visualisation using OpenPose and EasyMocap

# Get a free port to run the OpenPose container with
OPENPOSE_PORT=$(python -c 'import socket; s=socket.socket(); s.bind(("", 0)); print(s.getsockname()[1]); s.close()')

# The OpenPose container waits for commands from the EasyMocap container
srun apptainer run \
    --nv \
    --containall \
    --bind "${DATA_DIRECTORY}"/Rec${RECORDING_NUMBER}_processed:"${CONTAINER_DATA_DIRECTORY}" \
    $OPENPOSE_IMAGE --openpose_port $OPENPOSE_PORT &

data=/home/user/easymocap/EasyMocap/data/examples/_data

# Wait for the OpenPose container to start, otherwise we might get connection errors
sleep 30

srun apptainer run \
    --nv \
    --containall \
    --cwd /home/user/easymocap/EasyMocap \
    --bind "${DATA_DIRECTORY}"/Rec${RECORDING_NUMBER}_processed:"${CONTAINER_DATA_DIRECTORY}" \
    $EASYMOCAP_IMAGE \
    python apps/preprocess/extract_keypoints.py ${data} \
      --mode openpose \
      --hand \
      --face \
      --ext .png \
      --shutdown_openpose \
      --openpose_port $OPENPOSE_PORT \
      --folder_to_process $CAMERA_TO_PROCESS &

wait
