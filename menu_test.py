#!/usr/bin/env python
# coding: Latin-1

# Load library functions we want


import os
import sys
from inputs import get_gamepad
import time
import subprocess
import socket
import fcntl
import struct
import PicoBorgRev

# Re-direct our output to standard error, we need to ignore standard out to hide some nasty print statements from pygame
sys.stdout = sys.stderr

# Setup the PicoBorg Reverse
PBR = PicoBorgRev.PicoBorgRev()
#PBR.i2cAddress = 0x44                  # Uncomment and change the value if you have changed the board address
PBR.Init()
if not PBR.foundChip:
    boards = PicoBorgRev.ScanForPicoBorgReverse()
    if len(boards) == 0:
        print ('No PicoBorg Reverse found, check you are attached ')
    else:
        print ('No PicoBorg Reverse at address %02X, but we did find boards:' % (PBR.i2cAddress))
        for board in boards:
            print ('    %02X (%d)' % (board, board))
        print ('If you need to change the I2C address change the setup line so it is correct, e.g.')
        print ('PBR.i2cAddress = 0x%02X' % (boards[0]))
    sys.exit()
    # PBR.SetEpoIgnore(True)                 # Uncomment to disable EPO latch, needed if you do not have a switch / jumper
    # Ensure the communications failsafe has been enabled!
    failsafe = False
    for i in range(5):
        PBR.SetCommsFailsafe(True)
        failsafe = PBR.GetCommsFailsafe()
        if failsafe:
            break
    if not failsafe:
        print 'Board %02X failed to report in failsafe mode!' % (PBR.i2cAddress)
        sys.exit()
    PBR.ResetEpo()

# Power settings
voltageIn = 12.4                        # Total battery voltage to the PicoBorg Reverse
voltageOut = voltageIn*0.95              # Maximum motor voltage, we limit it to 95% to allow the RPi to get uninterrupted power

# Setup the power limits
if voltageOut > voltageIn:
    maxPower = 1.0
else:
    maxPower = voltageOut / float(voltageIn)

manual_mode_lock_flag = True
second_press_to_comfirm_flag = False

menu_flag = True
exit_flag = True

option_selected = "none"

options_key = ['Manual Mode', 'Line Following', 'Maze', 'Speed Run', 'Kicker', 'Radio', 'Shutdown', 'Reboot','Exit',
           'I P address']
options_module = {'Manual Mode': False, 'Line Following': False, 'Maze': False, 'Speed Run': False, 'Kicker': False,
                  'Radio': False, 'Shutdown': False, 'Reboot': False,'I P address': False, 'Exit': False}

menu_position_flag = 0

power_left = 0.0
power_right = 0.0
x_axis = 0.0
y_axis = 0.0


def mixer(inYaw, inThrottle,):
    left = inThrottle + inYaw
    right = inThrottle - inYaw
    scaleLeft = abs(left / 125.0)
    scaleRight = abs(right / 125.0)
    scaleMax = max(scaleLeft, scaleRight)
    scaleMax = max(1, scaleMax)
    out_left = int(constrain(left / scaleMax, -125, 125))
    out_right = int(constrain(right / scaleMax, -125, 125))
    results = [out_right, out_left]
    return results

def constrain(val, min_val, max_val):
    return min(max_val, max(min_val, val))


def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])

def lineFollow():

    line_follow_flag = True
    while line_follow_flag:

        print("#### line following ####")

def maze():

    maze_flag = True
    while maze_flag:

        print("#### maze ####")

def speed():

    speed_flag = True
    while speed_flag:

        print("#### speed ####")

def speakIPAddress():
    wlan = get_ip_address('wlan0')
    command = "flite -voice rms -t 'My I P address is " + wlan + "' "
    print command
    os.system(command)


speakIPAddress()



# main menu

try:
    print 'Press CTRL+C to quit'

    loopCount = 0

    # Loop indefinitely
    while exit_flag:
        events = get_gamepad()
        #print events
        #print loopCount
        #loopCount = loopCount + 1

        for event in events:
            #print(event.code, event.state)

            if menu_flag:


                if event.code == "BTN_EAST":
                    if event.state == True:
                        print("Cross")
                        second_press_to_comfirm_flag = False
                        command = 'flite -voice rms -t "I am afraid I can\'t do that Dave" '
                        print command
                        os.system(command)

                if event.code == "BTN_C":
                    if event.state == True:
                        print("Circle")
                        if second_press_to_comfirm_flag:
                            command = "flite -voice rms -t '" + options_key[menu_position_flag] + " comfirmed' "
                            os.system(command)
                            menu_flag = False
                            options_module[options_key[menu_position_flag]] = True

                            print ("Passed to " + options_key[menu_position_flag])

                            second_press_to_comfirm_flag = False
                        else:
                            os.system("flite -voice rms -t 'press again to comfirm " + options_key[menu_position_flag] + " or cross to exit ' ")
                            second_press_to_comfirm_flag = True

                if event.code == "BTN_TR2":
                    if event.state == True:
                        print("Start")
                        if manual_mode_lock_flag:
                            os.system("flite -voice rms -t 'Manual Mode Lock off' ")
                            manual_mode_lock_flag = False
                        else:
                            os.system("flite -voice rms -t 'Manual Mode Lock on' ")
                            manual_mode_lock_flag = True

                if event.code == "BTN_TL2":
                    if event.state == True:
                        print("Select")
                        print(menu_position_flag)
                        command = "flite -voice rms -t '" + options_key[menu_position_flag] + "' &"
                        os.system(command)
                if event.code == "ABS_HAT0Y":
                    if event.state == -1:
                        print("D pad Up")
                        if menu_position_flag == len(options_key)-1:
                            menu_position_flag = 0
                        else:
                            menu_position_flag = menu_position_flag + 1


                    elif event.state == 1:
                        print("D pad Down")
                        if menu_position_flag == 0:
                            menu_position_flag = len(options_key)-1
                        else:
                            menu_position_flag = menu_position_flag - 1
                    if event.state == 1 or event.state == -1:
                        print(menu_position_flag)
                        print options_key[menu_position_flag]
                        command = "flite -voice rms -t '" + options_key[menu_position_flag] + "' "
                        print command
                        os.system(command)
                        second_press_to_comfirm_flag = False
                if event.code == "ABS_HAT0X":
                    if event.state == -1:
                        print("D pad Left")
                    elif event.state == 1:
                        print("D pad Right")
                if event.code == "BTN_Z":
                    if event.state == True:
                        print("Top right")
                        os.system("python /home/pi/randomFart.py &")
                if event.code == "BTN_MODE":
                    if event.state == True:
                        print("Home")
                        os.system("flite -voice rms -t 'Home Menu.'")
                        if manual_mode_lock_flag:
                            os.system("flite -voice rms -t 'Manual Mode Lock on' ")
                        else:
                            os.system("flite -voice rms -t 'Manual Mode Lock off.' ")
                        os.system("flite -voice rms -t 'use up down on the D Pad to select option, then press circle to select.' ")


                print("#### Menu ####")

            # print(event.ev_type, event.code, event.state)

# manual mode

            if options_module['Manual Mode']:
                if event.code == "ABS_Y":
                    if event.state > 130:
                        print("Backwards")
                    elif event.state < 125:
                        print("Forward")
                    y_axis = event.state
                    if y_axis > 130:
                        y_axis = -(y_axis - 130)
                    elif y_axis < 125:
                        y_axis = ((-y_axis) + 125)
                    else:
                        y_axis = 0.0
                    print("Y: " + str(-y_axis))
                if event.code == "ABS_Z":
                    if event.state > 130:
                        print("Right")
                    elif event.state < 125:
                        print("Left")
                    x_axis = event.state
                    if x_axis > 130:
                        x_axis = (x_axis - 130)
                    elif x_axis < 125:
                        x_axis = -((-x_axis) + 125)
                    else:
                        x_axis = 0.0
                    print("X: " + str(x_axis))

                if event.code == "BTN_TL":
                    if event.state == True:
                        print("Turbo")
                if event.code == "BTN_TR":
                    if event.state == True:
                        print("Tank")
                if event.code == "BTN_Z":
                    if event.state == True:
                        print("Top right")
                        os.system("python /home/pi/randomFart.py &")
                if event.code == "BTN_WEST":
                    if event.state == True:
                        print("Top left")
                        os.system("play /home/pi/Sounds/squirrel01.mp3 &")
                if event.code == "BTN_TL2":
                    if event.state == True:
                        print("Select")
                        menu_flag = True
                        options_module['Manual Mode'] = False
                        print("Manual Mode Exit")
                        os.system("flite -voice rms -t 'Manual Mode Exit' ")
                        x_axis = 0
                        y_axis = 0

                mixer_results = mixer(x_axis, y_axis)
                print (mixer_results)
                power_left = mixer_results[0] / 125.0
                power_right = mixer_results[1] / 125.0
                print("left: " + str(power_left) + " right: " + str(power_right))

                PBR.SetMotor1((-power_right * maxPower))
                PBR.SetMotor2 (power_left * maxPower)

                print("#### Manual ####")

# line following

            if options_module['Line Following']:
                lineFollow()
                menu_flag = True
                options_module['Line Following'] = False
                print("Line Following Exit")

# Speed run

            if options_module['Speed Run']:
                speed()
                options_module['Speed Run'] = False
                menu_flag = True
                print("#### speed run ####")

# maze

            if options_module['Maze']:
                maze()
                options_module['Maze'] = False
                menu_flag = True
                print("Maze exit")

# kicker

            if options_module['Kicker']:
                options_module['Kicker'] = False
                menu_flag = True
                print("#### kicker ####")
# radio
            if options_module['Radio']:
                options_module['Radio'] = False
                menu_flag = True
                #subprocess.call("play /home/pi/Sounds/8bit/", shell=True)
                print("#### Radio ####")
# shutdown
            if options_module['Shutdown']:

                print("#### Good Bye ####")
                command = "flite -voice rms  daisy.txt "
                print command
                os.system(command)
                time.sleep(3)
                command = "flite -voice rms  -t 'Goodbye Dave' "
                print command
                os.system(command)
                time.sleep(1)
                options_module['Shutdown'] = False
                menu_flag = True
                subprocess.call("sudo halt", shell=True)

# ip address
            if options_module['I P address']:
                options_module['I P address'] = False
                menu_flag = True

                speakIPAddress()
                print("#### IP Address ####")
# reboot
            if options_module['Reboot']:
                options_module['Reboot'] = False
                menu_flag = True
                command = "flite -voice rms -t 'My system is rebooting in 5' "
                print command
                os.system(command)
                for i in range(4,0,-1):

                    command = "flite -voice rms -t \'" + str(i) + " \'"
                    print command
                    os.system(command)
                    time.sleep(0.98)
                command = "flite -voice rms -t 'rebooting now!' "
                print command
                os.system(command)
                time.sleep(1)

                print("#### restarting ####")
                subprocess.call("sudo reboot", shell=True)

# exit to command line
            if options_module['Exit']:
                options_module['Exit'] = False
                exit_flag = False


                print("#### exiting to command line ####")




except KeyboardInterrupt:

    # CTRL+C exit, disable all drives
    print("\nstopping")
    PBR.SetMotor1(0)
    PBR.SetMotor2(0)

os.system("flite -voice rms -t 'Exiting to the Command line' ")
print("bye")