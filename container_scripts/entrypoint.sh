#!/bin/bash

# data=/home/user/easymocap/EasyMocap/data/examples/revise_two_1_5_seconds/

data=$1
python scripts/preprocess/extract_video.py ${data} --no2d
python apps/preprocess/extract_keypoints.py ${data} --mode openpose --hand --face
python apps/demo/mvmp.py ${data} --out ${data}/output --annot annots ---cfg config/exp/mvmp1f.yaml --undis --vis_det --vis_repro