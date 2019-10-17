#!/bin/bash
INSTALL_PATH=$(dirname $(dirname $(readlink -f `which $0`)))
python3 $INSTALL_PATH/src/driver.py $@
