#!/usr/bin/env bash
# exit on error
set -o errexit

# Install Python dependencies
pip install -r requirements.txt

# Install FFmpeg using sudo for administrative privileges
sudo apt-get update && sudo apt-get install -y ffmpeg
