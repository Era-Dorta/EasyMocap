#!/bin/bash
REPO_DIR=$(dirname $(dirname $(realpath $0)))

cd $REPO_DIR

docker build \
    --progress=plain \
    --target runtime \
    --tag local/easymocap:pytorch2.2.0-cuda12.1 \
    ${REPO_DIR}