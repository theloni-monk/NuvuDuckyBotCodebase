import time
import cv2
import os
import numpy as np
# Import library that allows parallel processing
from multiprocessing import Process, Queue
# Import library for streaming video
import streamServerDependency.streamserver
# Import the pipeline code
import sys
# Import the debug constant
from config import *
import socket


#THIS RUNS AN IMAGE THROUGH THE PIPELINE
# NOTE: THE PIPELINE WILL RETURN A MARKED UP IMAGE AND OUTPUT TO THE MOTORS OVER A QUEUE
# FURTHER NOTE: this function runs pipeline because it needs to encapsulate everything passed to the streaming server
def retrieveImage(pipeline, cam, motorq):
    # read a frame from the camera
    ret, frame = cam.read()
    if not ret:
        # return a black frame when the camera retrieves no frame
        return np.zeros()
    frame = pipeline(frame, motorq) 
    return frame

#COREPROCESS runs the videostream and the motor outputs through the pipeline function
def coreProcess(pipelineFunc, motorq, cmdq):
    #THIS CODE SETS UP CAMERA THEN BEGINS VIDEOSTREAMING SERVER:
    server = None
    disconnected = True
    # streaming enabled
    if not DISABLE_STREAMING and not DISABLE_STREAMING_AND_ENABLE_WINDOW:
        server = streamServerDependency.streamserver.Server(port=5000, verbose = VERBOSE) #promoteErrors = True by defualt,
        server.initSock()
        server.s.settimeout(10)
        disconnected = True 
    # streaming disabled and window enabled  
    elif DISABLE_STREAMING_AND_ENABLE_WINDOW:
        cv2.namedWindow("DuckyBot Camera Feed", cv2.WINDOW_NORMAL)
        print "to close the window, press q or esc, but the program will not exit"

    cam = cv2.VideoCapture(0) #TODO: use rpistream camera object
    cam.set(3, CAM_WIDTH)
    cam.set(4, CAM_HEIGHT)
    
    try: #catch keyboard interrupts
        while True:
            #THE CMDQ IS USED TO COMMUNICATE TO THE STREAMPROCESS THAT IT NEEDS TO STOP

            # we are now in the core loop, check if we should exit:
            msg = None
            # Get the most recent message
            while not cmdq.empty():
                msg = cmdq.get()#block=False)
            # Check if the message is None or "exit"
            if msg is None:
                pass
            elif msg == 'exit':
                print "core process exiting cleanly"
                return

            #PERSISTANT STREAMING CODE
            if not DISABLE_STREAMING and not DISABLE_STREAMING_AND_ENABLE_WINDOW:
                if disconnected:
                    try:
                        print "attempting connection"
                        server.serve() #blocking serve for 5s
                        #server.s.settimeout(10) #TODO: set timeout from inside streamserver
                        print "serving successful"
                        initImg = retrieveImage(pipelineFunc, cam, motorq)
                        print "initImg retrieved"
                        server.initializeStream(initImg)
                        print "stream initialized"
                        disconnected = False
                    except socket.error as exc: #HACK: this is awful!
                        print(exc)
                        disconnected = True
                else:
                    try:
                        server.sendFrame(server.fetchFrame(
                                retrieveImage, [pipelineFunc, cam, motorq]))
                    except Exception as exc:
                        print(exc)
                        disconnected = True    

            #VNC WINDOW CODE
            elif DISABLE_STREAMING_AND_ENABLE_WINDOW:
                cv2.imshow("DuckyBot Camera Feed", retrieveImage(pipelineFunc, cam, motorq)) # shows pipeline output in window to be viewed over vnc
                k = cv2.waitKey(1)
                if k == ord('q') or k == 27: # q or esc
                    cmdq.put('exit')

            #AUTONOMOUS CODE
            else:
                retrieveImage(pipelineFunc, cam, motorq) # runs pipline

    except BaseException as exc:
        print "core closed on error"
        if VERBOSE: 
            print exc
        cam.release()
        return
