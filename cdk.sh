#!/bin/bash -eu
PROJECT_ROOT=$(cd $(dirname $0); pwd)
cd ${PROJECT_ROOT}

docker run \
  --rm \
  -it \
  -v ${PWD}:/opt/cdk \
  -v ${HOME}/.aws:/root/.aws:ro \
  cdk-template-v2:latest cdk $*
