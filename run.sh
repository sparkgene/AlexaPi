#!/bin/bash

. /home/pi/.bashrc
eval "$(pyenv init -)"

echo "a"

eval "$(pyenv virtualenv-init -)"

echo "b"

pyenv activate alexa

echo "c"

cd /home/pi/AlexaPi
python wakeword_detection.py
