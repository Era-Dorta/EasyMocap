#!/bin/bash

# This is the multi-vew multiple people video demo from https://github.com/zju3dv/EasyMocap/blob/master/doc/mvmp.md
data=/home/user/easymocap/EasyMocap/data/examples/_data
python scripts/preprocess/extract_video.py ${data} --no2d
python apps/preprocess/extract_keypoints.py ${data} --mode openpose --hand --face
python apps/demo/mvmp.py ${data} --out ${data}/output --annot annots --cfg config/exp/mvmp1f.yml --undis --vis_det --vis_repro