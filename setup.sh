#!/bin/bash

python3 -m venv hhsmartmirror
hhsmartmirror/bin/python -m pip install --upgrade pip setuptools wheel
source ./hhsmartmirror/bin/activate
pip install -r requirements.txt
pip install --global-option='build_ext' --global-option='-I/usr/local/include' --global-option='-L/usr/local/lib' pyaudio
