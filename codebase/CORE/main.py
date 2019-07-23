#!/usr/bin/python
import motor
import gamepad
# Import library that allows parallel processing
from multiprocessing import Process, Queue
# Import library that ensures an exist function is called when Python stops.
import atexit
# Import OpenCV
import cv2
import time
import CORE
import parameters


##########################################
# MAIN CODE
##########################################


def start(pipelineFunc):
    # Create a queue to communicate to the motor process.
    motorq = Queue()
    # Create a Process that runs the motors, give it the queue.
    motorp = Process(target=motor.motorProcess, args=(motorq,))
    # Start the motorPorcess
    motorp.start()

    # Create a queue to communicate to the video process.
    cmdq = Queue()

    # Create a queue to communicate to the gamepad process.
    if not parameters.BYPASS_GAMEPAD:
        gamepadq = Queue()
        # Create a Process for the gamepad, and give it the gamepad queue.
        gamepadp = Process(target=gamepad.gamepadProcess,
                        args=(pipelineFunc, gamepadq, motorq, cmdq))
        # Start the gamepadProcess
        gamepadp.start()
    else:
        # Create a Process for the camera, and give it the video queue.
        corep = Process(target = CORE.coreProcess, args=(pipelineFunc, motorq, cmdq))
        # Start the videoProcess
        corep.start()

    # Register the exitFunction() to be called when this Python script ends.
    atexit.register(exitFunction)

    # Prevent this main process from terminating until ESCAPE is pressed
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    # call the exit function
    exitFunction(gamepadq, gamepadp, motorq, motorp, cmdq, corep)

def exitFunction(gq, gp, mq, mp, cmdq, cp):
    # Send a sign to the gamepadProcess to end
    gq.put("exit")
    # Wait for the gamepadProcess to end
    gp.join()
    print "gamepad process exit"
    # Send a sign to the motorProcess to end
    mq.put("exit")
    # Wait for the motor process to end
    mp.join()
    print "motor process exit"
    # Kill all the motors
    motor.turnOffMotors()
    # send command to kill core process
    cmdq.put("exit")
    # wait for process to end
    cp.join()
    print "core process exit"
    # Close any openCV windows
    #cv2.destroyAllWindows()
