#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tinkerforge.ip_connection import IPConnection
from tinkerforge.bricklet_distance_ir import BrickletDistanceIR
from tinkerforge.bricklet_dual_button import BrickletDualButton
from tinkerforge.bricklet_dual_relay import BrickletDualRelay
from tinkerforge.bricklet_oled_128x64 import BrickletOLED128x64
from resettabletimer import ResettableTimer
import os
import sys
import pygame
import time
import socketio

HOST = "localhost"
PORT = 4223
UID = "xpN"  # UID of Distance IR Bricklet
UID_dual_button = "mMX"
UID_dual_relay = "E8x"
UID_oled = "yqA"

isObjectPresent = False
objCount = 0

ipcon = IPConnection()  # Create IP connection
dir = BrickletDistanceIR(UID, ipcon)  # Create device object
db = BrickletDualButton(UID_dual_button, ipcon)
m_relay = BrickletDualRelay(UID_dual_relay, ipcon)  # Create device object
display = BrickletOLED128x64(UID_oled, ipcon)
pygame.mixer.init(44100, -16, 2, 1024)
sound = pygame.mixer.Sound('laser.wav')
denied_sound = pygame.mixer.Sound('denied.wav')
backend_connected = False
user_logged_in = False
user_name = ""
last_object = ""


def timeout():
    global isObjectPresent
    timer.cancel()
    if isObjectPresent:
        print("object out")
        isObjectPresent = False
        db.set_led_state(not isObjectPresent, not backend_connected)


timer = ResettableTimer(0.5, timeout)


def dummy_callback(param):
    global isObjectPresent
    global objCount
    global backend_connected
    global last_object
    timer.reset()
    if not isObjectPresent:
        sound.play()
        timer.start()
        objCount += 1
        m_relay.set_monoflop(1, True, 200)
        print("object in, count: " + str(objCount))
        isObjectPresent = True
        db.set_led_state(not isObjectPresent, not backend_connected)
        os.system("pkill -USR1 raspistill")
        last_object = "..."
        display.write_line(5, 0, last_object + "                  ")
        display.write_line(7, 0, "Object Count: " + str(objCount))


def main():
    print("connect to tinkerforge deamon")

    sys.stdout.flush()
    ipcon.connect(HOST, PORT)  # Connect to brickd
    # Don't use device before ipcon is connected
    display.clear_display()
    display.write_line(0, 0, "PINT - Pet Collector")
    display.write_line(2, 0, "Please Scan QR Code")
    display.write_line(7, 0, "Object Count: " + str(objCount))

    m_relay.set_state(False, False)
    dir.set_debounce_period(400)

    # distance in mm
    dir.set_distance_callback_threshold(BrickletDistanceIR.THRESHOLD_OPTION_SMALLER, 150, 0)
    dir.register_callback(BrickletDistanceIR.CALLBACK_DISTANCE_REACHED, dummy_callback)
    sio = socketio.Client()

    @sio.event
    def connect():
        global isObjectPresent
        global backend_connected
        print('connection to backend established')
        backend_connected = True
        db.set_led_state(not isObjectPresent, not backend_connected)

    @sio.event
    def disconnect():
        global isObjectPresent
        global backend_connected
        print('disconnected from server')
        backend_connected = False
        db.set_led_state(not isObjectPresent, not backend_connected)

    @sio.on('login_info')
    def login_info(data):
        global user_logged_in
        global user_name
        print('user logged in ', data)
        user_logged_in = True
        user_name = data['UserID']
        display.write_line(2, 0, "                       ")
        display.write_line(2, 0, "User " + str(user_name) + " logged in")

    @sio.on('logout_info')
    def logout_info(data):
        global user_logged_in
        global user_name
        print('user logged out ', data)
        user_logged_in = False
        user_name = ""
        display.write_line(2, 0, "                         ")
        display.write_line(2, 0, "Please Scan QR Code")

    @sio.on('bottle inserted')
    def bottle_inserted(data):
        global last_object
        last_object = data['matches']
        # print('object analyzed ', data)
        last_object = data['matches'][0]['description']
        print('object analyzed', last_object)
        display.write_line(5, 0, "                         ")
        display.write_line(5, 0, last_object)
        #if last_object == 'Objekt nicht erkannt':
        denied_sound.play()

    sio.connect('wss://shrouded-inlet-73857.herokuapp.com/')
    # keep application running
    sio.wait()
    ipcon.disconnect()


main()
