#!/bin/bash
REPO_DIR=$(dirname $(dirname $(realpath $0)))

cd $REPO_DIR

VERSION=$(grep -oP "(?<=    version=')[^']*" setup.py)

apptainer build easymocap-${VERSION}.sif docker-daemon:docker.io/eradorta/easymocap:${VERSION}
