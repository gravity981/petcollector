#!/bin/sh

echo "start camera service"
mkdir -p /home/pi/camera_data
raspistill -t 1 -md 4 -w 1012 -h 760 -ex off --shutter 1000 -o /home/pi/camera_data/Image.jpg -s
