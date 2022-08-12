#!/bin/bash

ROOT_DIR=$(dirname $0)/..

mkdir -p $ROOT_DIR/docs

#sphinx-apidoc -fF -o $ROOT_DIR/docs $ROOT_DIR/src
#sphinx-apidoc -fF -o $ROOT_DIR/docs $ROOT_DIR/src/actions
sphinx-apidoc -f -o $ROOT_DIR/docs $ROOT_DIR/src/actions

pushd $ROOT_DIR/docs

make html
