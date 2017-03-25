#!/usr/bin/env python
# coding: Latin-1

# Load library functions we want


from inputs import get_gamepad


# Power settings
voltageIn = 12.4                        # Total battery voltage
voltageOut = voltageIn*0.95              # Maximum motor voltage, limited it to 95% to allow the RPi to get uninterrupted power

# Setup the power limits
if voltageOut > voltageIn:
    maxPower = 1.0
else:
    maxPower = voltageOut / float(voltageIn)

power_left = 0.0
power_right = 0.0
x_axis = 0.0
y_axis = 0.0


exit_flag = True


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

# main loop

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

            # print(event.ev_type, event.code, event.state)

# manual mode

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
            if event.code == "BTN_WEST":
                if event.state == True:
                    print("Top left")
            if event.code == "BTN_TL2":
                if event.state == True:
                    print("Select")

                    x_axis = 0
                    y_axis = 0

            mixer_results = mixer(x_axis, y_axis)
            print (mixer_results)
            power_left = mixer_results[0] / 125.0
            power_right = mixer_results[1] / 125.0
            print("left: " + str(power_left) + " right: " + str(power_right))
            '''

            set the motor speeds for your driver board here

            Set Motor 1 ((-power_right * maxPower))
            Set Motor 2 (power_left * maxPower)

            '''


            print("#### Manual ####")



except KeyboardInterrupt:

    # CTRL+C exit, disable all drives
    print("\nstopping")
    PBR.SetMotor1(0)
    PBR.SetMotor2(0)

print("bye")