echo "#####################################################"
echo "Please run 'python setup.py develop && cd /workspace/library/pymatch && python setup.py develop' in the container"
echo "#####################################################"

       # -v $(pwd):/workspace \

docker run -it \
       --gpus all -e DISPLAY=:1 \
       -v /tmp/.X11-unix:/tmp/.X11-unix \
       local/easymocap:pytorch2.2.0-cuda12.1 \
       /bin/bash
