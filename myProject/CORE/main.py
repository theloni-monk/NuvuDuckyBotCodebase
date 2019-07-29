#!/usr/bin/python
import motor
import gamepad
# Import library that allows parallel processing
import multiprocessing
from multiprocessing import Process, Queue
# Import library that ensures an exist function is called when Python stops.
import atexit
# Import OpenCV
import cv2
import sys
import time
import CORE
import config


##########################################
# MAIN CODE
##########################################
motorq = Queue()
motorp = Process()
gamepadq = Queue()
gamepadp = Process()
# Create a queue to communicate to the video process.
cmdq = Queue()
corep = Process()


def start(pipelineFunc):
    # Create a queue to communicate to the motor process.
    global motorp, gamepadp, corep
    if not config.DISABLE_MOTORS:
        # Create a Process that runs the motors, give it the queue.
        motorp = Process(target=motor.motorProcess, args=(motorq,))
        # Start the motorPorcess
        motorp.start()
        print "main process created motor process, pid = " + str(motorp.pid)

    # Create a queue to communicate to the gamepad process.
    if not config.DISABLE_GAMEPAD:

        # Create a Process for the gamepad, and give it the gamepad queue.
        gamepadp = Process(target=gamepad.gamepadProcess,
                           args=(pipelineFunc, gamepadq, motorq, cmdq))
        # Start the gamepadProcess
        gamepadp.start()
        print "main process created gamepad process, pid = " + \
            str(gamepadp.pid)
        # Register the exitFunction() to be called when this Python script ends.
        # atexit.register(exitFunction,[])
    else:  # bypass gamepad:
        # Create a Process for the camera, and give it the video queue.
        corep = Process(target=CORE.coreProcess,
                        args=(pipelineFunc, motorq, cmdq))
        # Start the videoProcess
        corep.start()
        print "main process created core process, pid = " + str(corep.pid)
        # Register the exitFunction() to be called when this Python script ends.
        # atexit.register(exitFunction,[])

    # Prevent this main process from terminating until ESCAPE is pressed
    print "to exit, type 'q' and press enter, or press command and c at the same time"
    try:
        while True:
            k = raw_input()
            if k == 'q':  # q or esc
                break
    except KeyboardInterrupt as exc:
        print "main process closing on keyboard interrupt"
        if config.VERBOSE:
            print exc

    try:
        exitFunction()
    except BaseException as exc:  # catch interrupt or multiprocessing error
        if config.VERBOSE:
            print exc

    # sys.exit(0)  # should call correct exit func
    return


def exitFunction():
    global motorq, motorp, gamepadq, gamepadp, cmdq, corep

    motorq.put("exit")
    # Wait for the motor process to end
    if motorp.is_alive():
        motorp.join()
    print "motor process exit"
    # Kill all the motors

    # send command to kill controller process
    gamepadq.put("exit")
    # wait for process to exit
    if gamepadp.is_alive():
        gamepadp.join()
    print "controller process exit"

    # send command to kill core process
    cmdq.put("exit")

    # wait for process to end
    if corep.is_alive():
        corep.join()
        print "core process exit"
    else:
        print "waiting for core process exit, 3 seconds"
        # wait for process to end even indirectly
        s = time.time()
        while time.time() < s+3:
            pass
        print "volitile core process exit, possible orphans"

    return
