#!/bin/sh
#SBATCH --job-name="easymocap"
#SBATCH --account=ewi-insy-reit
#SBATCH --partition=general
#SBATCH --ntasks=1 --cpus-per-task=1
#SBATCH --mem-per-cpu=16G
#SBATCH --gres=gpu
#SBATCH --time=10:00
#SBATCH --qos=short
#SBATCH --exclude=gpu[01-12],gpu[14-29]

# Open pose doesn't work on the A40 GPUs, so exclude them

export RECORDING_NUMBER=154
export EASYMOCAP_IMAGE="/tudelft.net/staff-umbrella/CaptureLab/Apptainer/easymocap-0.2.1.sif"
export OPENPOSE_IMAGE="/tudelft.net/staff-umbrella/CaptureLab/Apptainer/openpose-1.7.0.sif"
export DATA_DIRECTORY="/tudelft.net/staff-umbrella/CaptureLab/Recordings"

# The data directory inside the container
export CONTAINER_DATA_DIRECTORY=/home/user/easymocap/EasyMocap/data/examples/_data

# Run the containers with the following flags
# --nv to get access to the nvidia GPUs in the host system
# --containall to not mount any directory from the host system by default
# --bind mount the data directorie in the container
srun apptainer run \
    --nv \
    --containall \
    --bind "${DATA_DIRECTORY}"/Rec${RECORDING_NUMBER}_png:"${CONTAINER_DATA_DIRECTORY}" \
    $OPENPOSE_IMAGE &

srun apptainer run \
    --nv \
    --containall \
    --bind "${DATA_DIRECTORY}"/Rec${RECORDING_NUMBER}_png:"${CONTAINER_DATA_DIRECTORY}" \
    $EASYMOCAP_IMAGE  &

wait