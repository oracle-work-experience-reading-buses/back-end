#!/bin/bash

echo "NOTE: This script is designed to be ran on Raspberry Pi running the latest version of Raspbian (as of writing this) which is Buster."
echo "      If you're running this on a different device/operating system, don't expect it to work without modification."
echo ""

PACKAGES=("libportaudio2" "python3-numpy" "llvm" "cython" "libatlas-base-dev" "libsndfile1-dev" "libsamplerate0-dev" "cimg-dev" "ffmpeg" "libmpg123-dev" "libavcodec58" "libavcodec-extra58" "libavcodec-dev")
PIP_PACKAGES=("soundfile" "sounddevice" "librosa" "cython" "phash")
SOURCES=("http://mirror.ox.ac.uk/sites/archive.raspbian.org/archive/raspbian/pool/main/libp/libphash/libphash_0.9.4.orig.tar.gz")

echo "---------------------------------------------------"
echo "Raspbian packages"
echo "---------------------------------------------------"
for _package in "${PACKAGES[@]}"; do
	echo "Installing: ${_package}"
	echo "$(sudo apt-get install ${_package} -y)"
	echo ""
done

echo "Finished Raspbaian packages."

echo "---------------------------------------------------"
echo "Pip packages"
echo "---------------------------------------------------"

for _pip_package in "${PIP_PACKAGES[@]}"; do
	echo "Installing: ${_pip_package}"
	echo "$(sudo pip3 install ${_pip_package})"
	echo ""
done

echo "Finished Pip packages."

echo "---------------------------------------------------"
echo "Building from Source(s)"
echo "---------------------------------------------------"

# Just to make sure it's easier add multiple source complimations later?
# At the moment, the loop is specialised towards building the pHash 
# library.

for _source_url in "${SOURCES[@]}"; do
		echo "Downloading \"$_source_url\"..."
		file_name="${_source_url##*/}"
		dir_name=$(echo "$file_name" | sed 's/\(\.orig\.tar\.gz\)//g' | sed 's/\(lib\)//g' | sed 's/_/-/g' | sed 's/h/H/')
		curl "$_source_url" -o "$file_name"
		echo "Extracting \"$file_name\"..."
		tar -xvf "$file_name"
		echo "Compiling \"$dir_name\"..."
		cd "$dir_name"
		./configure --enable-video-hash=no && sudo make install
		cd ..
		exit_code="$?"
		if [[ "$exit_code" == "0" ]]; then
			echo "Compiled successfully!"
		else
			echo "Complimation failed."
		fi
		rm "$file_name"
		sudo rm -rf "$dir_name"
		echo ""
done


echo "Finished installing required libraries and packages."
