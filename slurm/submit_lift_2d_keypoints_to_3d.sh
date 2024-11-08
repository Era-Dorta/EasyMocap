#!/bin/sh
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=16G
#SBATCH --time=5:00
#SBATCH --qos=long

# 3D keypoint extraction and visualisation using EasyMocap
data=/home/user/easymocap/EasyMocap/data/examples/_data

# Run the containers with the following flags
# --nv to get access to the nvidia GPUs in the host system
# --containall to not mount any directory from the host system by default
# --bind mount the data directory in the container
apptainer run \
    --containall \
    --cwd /home/user/easymocap/EasyMocap \
    --bind "${DATA_DIRECTORY}"/Rec${RECORDING_NUMBER}_processed:"${CONTAINER_DATA_DIRECTORY}" \
    $OPENPOSE_IMAGE \
    python apps/demo/mvmp.py ${data} --out ${data}/output --annot annots --cfg config/exp/mvmp1f.yml --undis --vis_det --vis_repro
