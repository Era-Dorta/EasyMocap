#!/bin/bash

# This script is the multiple view with multiple people video demo from
# https://github.com/zju3dv/EasyMocap/blob/master/doc/mvmp.md

data=/home/user/easymocap/EasyMocap/data/examples/_data

# Images where already extracted by the capturesystem image
python scripts/preprocess/extract_video.py ${data} --no2d --end 1000000000
python apps/preprocess/extract_keypoints.py ${data} --mode openpose --hand --face
python apps/demo/mvmp.py ${data} --out ${data}/output --annot annots --cfg config/exp/mvmp1f.yml --undis --vis_det --vis_repro