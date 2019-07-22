import time
import cv2
import os
import numpy as np
# Import library that allows parallel processing
from multiprocessing import Process, Queue
# Import library for streaming video
from rpistream import streamserver
# Import the pipeline code
from pipeline import pipeline
# Import the debug constant
import parameters
import socket

#TODO: replace with rpistream camera
# Change the camera resolution, before the processes start
cam_width = 320
cam_height = 240
scale = 1

#THIS RUNS AN IMAGE THROUGH THE PIPELINE
# NOTE: THE PIPELINE WILL RETURN A MARKED UP IMAGE AND OUTPUT TO THE MOTORS OVER A QUEUE
# FURTHER NOTE: this function runs pipeline because it needs to encapsulate everything passed to the streaming server
def retrieveImage(cam, motorq):
    # read a frame from the camera
    ret, frame = cam.read()
    if not ret:
        # return a black frame when the camera retrieves no frame
        return np.zeros()
    frame = pipeline(frame, motorq) 
    return frame

#COREPROCESS runs the videostream and the motor outputs through the pipeline function
def coreProcess(motorq, cmdq):
    #THIS CODE SETS UP CAMERA THEN BEGINS VIDEOSTREAMING SERVER:
    
    server = streamserver.Server(port=5000, verbose=parameters.VERBOSE)
    disconnected = True
    cam = cv2.VideoCapture(0) #TODO: use rpistream camera
    cam.set(3, cam_width)
    cam.set(4, cam_height)

    while True:
        #THE CMDQ IS USED TO COMMUNICATE TO THE STREAMPROCESS THAT IT NEEDS TO STOP

        # we are now in the core loop, check if we should exit:
        msg = None
        # Get the most recent message
        while not cmdq.empty():
            msg = cmdq.get(block=False)
        # Check if the message is None or "exit"
        if msg is None:
            pass
        elif msg == 'exit':
            return
        if not parameters.BYPASS_STREAMING:
            try:
                if disconnected:
                    server.serveNoBlock() #blocking
                disconnected = False
                server.sendFrame(server.fetchFrame(
                    retrieveImage, [cam, motorq]))
            except socket.error as exc:
                print(exc)
                disconnected = True
        else:
            retrieveImage(cam, motorq) # runs pipline

    # release the camera
    cam.release()
