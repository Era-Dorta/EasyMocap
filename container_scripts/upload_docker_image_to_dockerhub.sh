#!/bin/bash
REPO_DIR=$(dirname $(dirname $(realpath $0)))

cd $REPO_DIR

VERSION=$(grep -oP "(?<=    version=')[^']*" setup.py)

docker login
docker push eradorta/easymocap:$VERSION-base
docker push eradorta/easymocap:$VERSION