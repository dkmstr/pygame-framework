#!/bin/bash

filename=$(basename "$1")
extension="${1##*.}"
filename="${1%.*}"

ffmpeg -i "$1" -c:a libvorbis -q:a 4 "$filename.ogg"
