#!/bin/bash

if [ $# -ne 1 ]; then
    echo "Must provide your github username as argument"
    exit 1
fi

REPO_DIR=$(dirname $(dirname $(realpath $0)))

cd $REPO_DIR

VERSION=$(grep -oP "(?<=    version=')[^']*" setup.py)

apptainer registry login --username $1 oras://ghcr.io
apptainer push easymocap-${VERSION}.sif oras://ghcr.io/era-dorta/easymocap:${VERSION}