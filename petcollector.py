#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tinkerforge.ip_connection import IPConnection
from tinkerforge.bricklet_distance_ir import BrickletDistanceIR
from tinkerforge.bricklet_dual_button import BrickletDualButton
from tinkerforge.bricklet_dual_relay import BrickletDualRelay
from resettabletimer import ResettableTimer
from subprocess import check_output
import os
import sys
import signal
import pygame
import time

HOST = "localhost"
PORT = 4223
UID = "xpN"  # UID of Distance IR Bricklet
UID_dual_button = "mMX"
UID_dual_relay = "E8x"

isObjectPresent = False
objCount = 0

ipcon = IPConnection()  # Create IP connection
dir = BrickletDistanceIR(UID, ipcon)  # Create device object
db = BrickletDualButton(UID_dual_button, ipcon)
m_relay = BrickletDualRelay(UID_dual_relay, ipcon)  # Create device object
m_raspistillPID = 0    #raspistill process id needed to send a camera trigger event
pygame.mixer.init(44100, -16, 2, 1024)
sound = pygame.mixer.Sound('laser.wav')


def timeout():
    global isObjectPresent
    timer.cancel()
    if isObjectPresent:
        print("object out")
        isObjectPresent = False
        db.set_led_state(BrickletDualButton.LED_STATE_OFF,BrickletDualButton.LED_STATE_OFF)


timer = ResettableTimer(0.1, timeout)


def dummy_callback(param):
    global isObjectPresent
    global objCount
    global m_raspistillPID
    timer.reset()
    if not isObjectPresent:
        sound.play()
        timer.start()
        objCount += 1
        m_relay.set_monoflop(1, True, 20)
        print("object in, count: " + str(objCount))
        isObjectPresent = True
        db.set_led_state(BrickletDualButton.LED_STATE_ON , BrickletDualButton.LED_STATE_ON )
        os.kill(m_raspistillPID, signal.SIGUSR1)

def getRaspistillPID():
    global m_raspistillPID
    m_raspistillPID = check_output(["pidof","raspistill"])

def main():
    print("connect to tinkerforge deamon")
    getRaspistillPID()
    print("Raspistill PID:" + str(m_raspistillPID))

    sys.stdout.flush()
    ipcon.connect(HOST, PORT)  # Connect to brickd
    # Don't use device before ipcon is connected

    m_relay.set_state(False, False)
    dir.set_debounce_period(100)

    # distance in mm
    dir.set_distance_callback_threshold(BrickletDistanceIR.THRESHOLD_OPTION_SMALLER, 150, 0)
    dir.register_callback(BrickletDistanceIR.CALLBACK_DISTANCE_REACHED, dummy_callback)

    # keep application running
    try:
        while True:
            time.sleep(10)
    except:
        ipcon.disconnect()


main()
