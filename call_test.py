from inputs import get_gamepad
import os
import sys
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
    results = [out_left, out_right]
    return results

def constrain(val, min_val, max_val):
    return min(max_val, max(min_val, val))

while True:
    events = get_gamepad()
    print(events)
    # print loopCount
    # loopCount = loopCount + 1

    for event in events:

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
                 x_axis = (x_axis -130)
             elif x_axis < 125:
                 x_axis = -((-x_axis)+125)
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
        if event.code == "BTN_TL2":
            if event.state == True:
                print("Select")


        mixer_results = mixer(x_axis, y_axis)
        print (mixer_results)
        power_left = mixer_results[0]/125.0
        power_right = mixer_results[1]/125.0
        print("left: " + str(power_left) + " right: " + str(power_right))

        PBR.SetMotor1(power_left * maxPower)
        PBR.SetMotor2(power_right * maxPower)
