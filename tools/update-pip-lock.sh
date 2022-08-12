#!/bin/bash

# based on https://zenn.dev/yhay81/articles/yhay81-202102-piplock

#cd $(realpath $(dirname $0)/..)

REQUIREMENTS=$1
if [ "" == "$REQUIREMENTS" ]; then
  REQUIREMENTS=requirements.txt
fi

VENV_DIR=.venv_temp_$(date +%s)
python3 -m venv $VENV_DIR
source $VENV_DIR/bin/activate
pip3 install -U pip wheel
pip3 install -r $REQUIREMENTS
(
echo "# auto generated by update-pip-lock.sh"
pip3 freeze
) >| $(basename $REQUIREMENTS .txt).lock
rm -rf $VENV_DIR
