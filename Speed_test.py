#!/usr/bin/python

""" ST VL6180X ToF range finder program
 - power explorer board with 3.3 V
 - explorer board includes pull-ups on i2c """

import sys
from ST_VL6180X import VL6180X
from time import sleep
import RPi.GPIO as GPIO  # Import GPIO functions
import multiplex

i2cbus = 1  # 0 for rev1 boards etc.
address_mux = 0x70

plexer = multiplex.multiplex(i2cbus)

"""-- Setup --"""
debug = False
if len(sys.argv) > 1:
    if sys.argv[1] == "debug":  # sys.argv[0] is the filename
        debug = True

# setup ToF ranging/ALS sensor
tof_address = 0x29
tof_sensor = VL6180X(address=tof_address, debug=False)
tof_sensor.get_identification()
if tof_sensor.idModel != 0xB4:
    print"Not a valid sensor id: %X" % tof_sensor.idModel
else:
    print"Sensor model: %X" % tof_sensor.idModel
    print"Sensor model rev.: %d.%d" % \
         (tof_sensor.idModelRevMajor, tof_sensor.idModelRevMinor)
    print"Sensor module rev.: %d.%d" % \
         (tof_sensor.idModuleRevMajor, tof_sensor.idModuleRevMinor)
    print"Sensor date/time: %X/%X" % (tof_sensor.idDate, tof_sensor.idTime)
tof_sensor.default_settings()

"""-- MAIN LOOP --"""
while True:
    readings = [0, 0, 0, 0, 0, 0]
    for ToFaddress in range(0, 6):
        plexer.channel(address_mux, ToFaddress)
        readings[ToFaddress] = tof_sensor.get_distance()

        sleep(0.01)
    print readings

    # turn it up to 11

    left_sensor = readings[4]
    right_sensor = readings[1]

    if left_sensor > 240 & right_sensor > 240:
        print("full speed ahead")

    if left_sensor == right_sensor:
        print("full speed ahead")

    if left_sensor > right_sensor:
        print("turn left")

    if right_sensor > left_sensor:
        print("turn right")




