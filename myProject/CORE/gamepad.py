#!/usr/bin/python
# Import the device reading library
from evdev import InputDevice, categorize, ecodes, KeyEvent, list_devices
import CORE
import config
import sys
# Import library that allows parallel processing
from multiprocessing import Process, Queue


# Get the name of the Logitech Device
def getInputDeviceByName(name):
    devices = [InputDevice(fn) for fn in list_devices()]
    for device in devices:
        if device.name == name:
            return InputDevice(device.fn)
    return None


# Import our gamepad.
gamepad = getInputDeviceByName('Logitech Gamepad F710')

# Keeps track of whether the coreprocess is running
coreRunning = False
corep = Process()


def clearQueue(q):
    while not q.empty():
        q.get(block=False)

# Process the GamePad


def gamepadProcess(pipelineFunc, gamepadq, motorq, cmdq):
    # Create variables to keep track of the joystick state.
    joyLR = 0
    joyUD = 0
    # Create variable to keep track of camera state
    global coreRunning, corep
    # Loop over the gamepad's inputs, reading it.
    try: # catch keyboard interrupts
        for event in gamepad.read_loop():
            # we are now in the gamepad loop, check if we should exit
            msg = None
            # Get the most recent message
            while not gamepadq.empty():
                msg = gamepadq.get(block=True)
            # Check if the message is None or "exit"
            if msg is None:
                pass
            if msg == "exit":
                # Quit this function if the message is None
                # This is the indicator to stop this function
                if coreRunning:
                    print("Controller process exiting")
                    coreRunning = False
                    cmdq.put('exit')
                    corep.join()
                return

            # continue processing gamepad values
            if event.type == ecodes.EV_KEY:
                keyevent = categorize(event)
                if keyevent.keystate == KeyEvent.key_down:
                    print(keyevent.keycode)
                    if 'BTN_START' in keyevent.keycode:
                        if coreRunning:
                            print("DISABLING AUTONOMOUS CONTROL")
                            # Turn the camera OFF
                            coreRunning = False
                            cmdq.put('exit')
                            corep.join()
                        else:
                            print("ENABLING AUTONOMOUS CONTROL")
                            if coreRunning:
                                coreRunning = False
                                cmdq.put('exit')
                                # corep.join()
                            clearQueue(cmdq)
                            # Turn the camera ON
                            coreRunning = True
                            # Create a Process for the camera, and give it the video queue.
                            corep = Process(
                                target=CORE.coreProcess, args=(pipelineFunc, motorq, cmdq))
                            # Start the videoProcess
                            corep.start()
                            print "gamepad process created core process, pid = " + str(corep.pid)

            elif event.type == ecodes.EV_ABS:
                if event.code == 0:
                    print('PAD_LR '+str(event.value))
                elif event.code == 1:
                    print('PAD_UD '+str(event.value))
                elif event.code == 2:
                    print('TRIG_L '+str(event.value))
                elif event.code == 3:
                    print('JOY_LR '+str(event.value))
                    joyLR = event.value
                    # Send a message to the motorProcess when the joystick moves.
                    motorq.put([joyUD+joyLR, joyUD-joyLR])
                elif event.code == 4:
                    print('JOY_UD '+str(event.value))
                    joyUD = event.value
                    # Send a message to the motorProcess when the joystick moves.
                    motorq.put([joyUD+joyLR, joyUD-joyLR])
                elif event.code == 5:
                    print('TRIG_R '+str(event.value))
                elif event.code == 16:
                    print('HAT_LR '+str(event.value))
                elif event.code == 17:
                    print('HAT_UD '+str(event.value))
                else:
                    pass
    except BaseException as exc:
        print "gamepad closing on error"
        if config.VERBOSE:
            print exc
        if coreRunning:
            cmdq.put('exit')
            corep.join()
        
        return
