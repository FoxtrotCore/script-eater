#!/bin/bash

PY_BIN=python3
PY_PATH=$(command -v $PY_BIN)

UPERM_BIN=uperm
UPERM_PATH=$(command -v $UPERM_BIN)

INSTALL_PATH=/opt/script-eater

#
# 1: Message tag mode:
#   - 1 Say with info tag
#   - 2 Say with error tag
#   - 3 Say with warning tag
#
function say(){
    MODE=""

    if   [[ $1 == 1 ]]; then
        MODE="INFO"
    elif [[ $1 == 2 ]]; then
        MODE="ERROR"
    elif [[ $1 == 3 ]]; then
        MODE="WARN"
    fi

    echo -e "[$MODE]: $2"
}

function dependency() {
  if [[ -z $1 ]]; then
    say 2 "$2 is not installed!\n\tPlease install it before installing script-eater!"
    exit 0
  else
    say 1 "$2 was found in: $1"
  fi
}

if [[ $USER != "root" ]]; then
  say 2 "Must run the installer as root!"
  exit 0
fi

dependency $PY_PATH $PY_BIN
dependency $UPERM_PATH $UPERM_BIN

if [[ -d $INSTALL_PATH ]]; then
  say 3 "script-eater was already installed!\n\tOverwriting..."
  rm -rf $INSTALL_PATH
else
  say 1 "Starting a fresh install of script-eater!"
fi

cd ../
mkdir -p $INSTALL_PATH/bin
mkdir -p $INSTALL_PATH/src
mkdir -p $INSTALL_PATH/config
mkdir -p $INSTALL_PATH/cache

cp -r ./bin $INSTALL_PATH
cp -r ./src/*.py $INSTALL_PATH/src
cp -r ./res/* $INSTALL_PATH/config

ln -f -s $INSTALL_PATH/bin/script-eater.sh /usr/bin/script-eater
ln -f -s $INSTALL_PATH/bin/script-eater-bot.sh /usr/bin/script-eater-bot

uperm -u ivo -g ivo -d $INSTALL_PATH -p 700 -r -y -s
