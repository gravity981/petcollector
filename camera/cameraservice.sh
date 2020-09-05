#!/bin/sh

echo "start camera service"
mkdir -p /home/pi/camera_data
raspistill -o /home/pi/camera_data/image.jpg -s
