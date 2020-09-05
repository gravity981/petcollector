#!/bin/sh

echo "start camera service"
mkdir -p /home/pi/camera_data

raspistill -t 0 -md 4 -w 1012 -h 760 -ex off --shutter 1000 -roi 0.15,0.4,0.6,0.45 -o /home/pi/camera_data/Image%d.jpg -s

