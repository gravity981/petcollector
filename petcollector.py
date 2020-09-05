#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tinkerforge.ip_connection import IPConnection
from tinkerforge.bricklet_distance_ir import BrickletDistanceIR
from tinkerforge.bricklet_dual_button import BrickletDualButton
from tinkerforge.bricklet_dual_relay import BrickletDualRelay
from tinkerforge.bricklet_lcd_128x64 import BrickletLCD128x64
from resettabletimer import ResettableTimer
from subprocess import check_output
import os
import sys
import signal
import pygame
import time
import socketio

HOST = "localhost"
PORT = 4223
UID = "xpN"  # UID of Distance IR Bricklet
UID_dual_button = "mMX"
UID_dual_relay = "E8x"
UID_lcd = "yqA"

isObjectPresent = False
objCount = 0

ipcon = IPConnection()  # Create IP connection
dir = BrickletDistanceIR(UID, ipcon)  # Create device object
db = BrickletDualButton(UID_dual_button, ipcon)
m_relay = BrickletDualRelay(UID_dual_relay, ipcon)  # Create device object
lcd = BrickletLCD128x64(UID_lcd, ipcon)
pygame.mixer.init(44100, -16, 2, 1024)
sound = pygame.mixer.Sound('laser.wav')


def timeout():
    global isObjectPresent
    timer.cancel()
    if isObjectPresent:
        print("object out")
        isObjectPresent = False
        db.set_led_state(BrickletDualButton.LED_STATE_OFF, BrickletDualButton.LED_STATE_OFF)


timer = ResettableTimer(0.5, timeout)


def dummy_callback(param):
    global isObjectPresent
    global objCount
    timer.reset()
    if not isObjectPresent:
        sound.play()
        timer.start()
        objCount += 1
        m_relay.set_monoflop(1, True, 200)
        print("object in, count: " + str(objCount))
        isObjectPresent = True
        db.set_led_state(BrickletDualButton.LED_STATE_ON, BrickletDualButton.LED_STATE_ON )
        os.system("pkill -USR1 raspistill")

def main():
    print("connect to tinkerforge deamon")

    sys.stdout.flush()
    ipcon.connect(HOST, PORT)  # Connect to brickd
    # Don't use device before ipcon is connected

    m_relay.set_state(False, False)
    dir.set_debounce_period(500)

    # distance in mm
    dir.set_distance_callback_threshold(BrickletDistanceIR.THRESHOLD_OPTION_SMALLER, 150, 0)
    dir.register_callback(BrickletDistanceIR.CALLBACK_DISTANCE_REACHED, dummy_callback)
    sio = socketio.Client()

    @sio.event
    def connect():
        print('connection to backend established')

    @sio.event
    def login_info(data):
        print('message received with ', data)
        lcd.write_line(1, 0, str(data))
        print(str(db.get_led_state()))

    @sio.event
    def disconnect():
        print('disconnected from server')

    sio.connect('wss://shrouded-inlet-73857.herokuapp.com/')
    # keep application running
    try:
        while True:
            time.sleep(10)
    except:
        ipcon.disconnect()


main()
