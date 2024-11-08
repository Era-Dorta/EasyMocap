#!/bin/sh
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem-per-cpu=16G
#SBATCH --time=5:00
#SBATCH --qos=long
#SBATCH --gres=gpu
#SBATCH --exclude=awi01,awi02,cor1

# Exclude the V100 GPUs. The mp4 that those GPUs generate are 4x larger than with the other GPUs

# 3D keypoint extraction and visualisation using OpenPose and EasyMocap

# The OpenPose container waits for commands from the EasyMocap container

# Run the containers with the following flags
# --nv to get access to the nvidia GPUs in the host system
# --containall to not mount any directory from the host system by default
# --bind mount the data directory in the container
apptainer run \
    --nv \
    --containall \
    --bind "${DATA_DIRECTORY}"/Rec${RECORDING_NUMBER}_processed:"${CONTAINER_DATA_DIRECTORY}" \
    $OPENPOSE_IMAGE &

data=/home/user/easymocap/EasyMocap/data/examples/_data

apptainer run \
    --nv \
    --containall \
    --cwd /home/user/easymocap/EasyMocap \
    --bind "${DATA_DIRECTORY}"/Rec${RECORDING_NUMBER}_processed:"${CONTAINER_DATA_DIRECTORY}" \
    $EASYMOCAP_IMAGE \
    python apps/preprocess/extract_keypoints.py ${data} --mode openpose --hand --face --ext .png --shutdown_openpose &

wait
