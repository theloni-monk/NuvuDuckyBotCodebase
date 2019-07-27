# NuVu NuvieTown Codebase

This repository contains the code necessary to start coding autonomous duckybots.
It is essentially a boilerplate for a duckybot project such that one can completely focus on the image processing and motor handling,
without being bogged down in image debugging woes and blocking io ineffeciencies

## Architectural Overview

_________________________

### There are 3 seperate simultanious processes within the code

The controller process, The core process, and The motor process

* The controller process handles inputs from the gamepad controller and directly controls the motors based on said inputs. It can also start or stop the core process.

* The motor process handles outputs to the physical motors and phyisically communicates with the motor controller board. It is sent commands from the pipeline telling it how quickly to drive each motor.

* The core process handles videostreaming and image processing. it takes images in, processes them through a pipeline function and then streams its output. At the end of the pipeline it sends commands to the motorprocess regarding how to control the motors.

## To Begin

_________________________

place your image processing code into the file `pipeline.py` and the run `main.py` script within the myProject folder

On your logitech G507 controller press start and once you get a message that the server is ready use the code hosted on rpistrem_videoclient to view a livestream from your duckybot

The function pipline within said file must return an image, and put motor values into the motorq

Codebase written by Theo Cooper, David Wang, and Ian Huang
