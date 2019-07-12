#!/bin/bash

echo "NOTE: This script is designed to be ran on Raspberry Pi running the latest version of Raspbian (as of writing this) which is Buster."
echo "      If you're running this on a different device/operating system, don't expect it to work without modification."
echo ""

PACKAGES=("libportaudio2" "python3-numpy")
PIP_PACKAGES=("soundfile" "sounddevice") 

for _package in "${PACKAGES[@]}"; do
	echo "Installing: ${_package}"
	echo "$(sudo apt-get install ${_package})"
	echo ""
done

for _pip_package in "${PIP_PACKAGES[@]}"; do
	echo "Installing: ${_pip_package}"
	echo "$(sudo pip3 install ${_pip_package})"
	echo ""
done
