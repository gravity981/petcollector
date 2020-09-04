#!/usr/bin/env python
# -*- coding: utf-8 -*-


from tinkerforge.ip_connection import IPConnection
from tinkerforge.bricklet_distance_ir import BrickletDistanceIR
from tinkerforge.bricklet_dual_button import BrickletDualButton
from resettabletimer import ResettableTimer
import sys

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
    timer.reset()
    if not isObjectPresent:
        timer.start()
        objCount += 1
        print("object in, count: " + str(objCount))
        isObjectPresent = True
        db.set_led_state(BrickletDualButton.LED_STATE_ON , BrickletDualButton.LED_STATE_ON )


def main():
    print("connect to tinkerforge deamon")
    sys.stdout.flush()
    ipcon.connect(HOST, PORT)  # Connect to brickd
    # Don't use device before ipcon is connected

    #dir.set_debounce_period(100)

    # distance in mm
    #dir.set_distance_callback_threshold(BrickletDistanceIR.THRESHOLD_OPTION_SMALLER, 300, 0)
    #dir.register_callback(BrickletDistanceIR.CALLBACK_DISTANCE_REACHED, dummy_callback)

    # distance analog
    # dir.set_analog_value_callback_threshold(BrickletDistanceIR.THRESHOLD_OPTION_SMALLER, 100, 0)
    # dir.register_callback(BrickletDistanceIR.CALLBACK_ANALOG_VALUE_REACHED, dummy_callback)

    # Get current distance
    # distance = dir.get_distance()
    # print("Distance: " + str(distance/10.0) + " cm")

    #input("Press key to exit\n")  # Use raw_input() in Python 2
    #sleep(3)

    ipcon.disconnect()


main()
