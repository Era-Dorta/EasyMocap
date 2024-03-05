docker run -it \
       --gpus all -e DISPLAY=:1 \
       -v /tmp/.X11-unix:/tmp/.X11-unix \
       -v $(pwd):/workspace \
       local/easymocap:pytorch2.2.0-cuda12.1 \
       /bin/bash
