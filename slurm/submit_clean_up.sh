#!/bin/sh
#SBATCH --ntasks=1
#SBATCH --time=1:00

srun rm -rf "${DATA_DIRECTORY}/Rec${RECORDING_NUMBER}_processed/images"