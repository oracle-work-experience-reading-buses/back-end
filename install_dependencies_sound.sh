#!/bin/bash

PACKAGES=("libportaudio2" "python3-pyaudio" "python3-numpy")

for _package in "${PACKAGES[@]}"; do
	echo "Installing: ${_package}"
	echo "$(sudo apt-get install ${_package})"
	echo ""
done
