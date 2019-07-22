# Import Adafruit Motor HAT Library
from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor
# Import additional libraries that support MotorHAT
import time
# Import library that allows parallel processing
from multiprocessing import Process, Queue


# recommended for auto-disabling motors on shutdown!
def turnOffMotors():
	mh.getMotor(1).run(Adafruit_MotorHAT.RELEASE)
	mh.getMotor(2).run(Adafruit_MotorHAT.RELEASE)
	mh.getMotor(3).run(Adafruit_MotorHAT.RELEASE)
	mh.getMotor(4).run(Adafruit_MotorHAT.RELEASE)

# Complete this function so:
# 1. values in the range 1 to 32768 make the motor spin forward faster and faster.
# 2. values in the range -1 to -32768 make the motor spin backward faster and faster.
# 3. any value equal to 0 makes the motor BRAKE.
# 4. any values less than -32768 and greater than 32768 use the max speed in the right direction.
def runMotor(motor, speed):
	""" motor - the motor object to control.
		speed - a number from -32768 (reverse) to 32768 (forward) """
	if speed < -32768:
		motor.setSpeed(255)
		motor.run(Adafruit_MotorHAT.BACKWARD)
	elif speed > 32768:
		motor.setSpeed(255)
		motor.run(Adafruit_MotorHAT.FORWARD)
	elif speed > 0:
		motor.setSpeed(int(speed/128.0))
		motor.run(Adafruit_MotorHAT.FORWARD)
	elif speed < 0:
		motor.setSpeed(int(speed/-128.0))
		motor.run(Adafruit_MotorHAT.BACKWARD)
	else:
		motor.setSpeed(0)
		motor.run(Adafruit_MotorHAT.BRAKE)


# create a default MotorHAT object, no changes to I2C address or frequency
mh = Adafruit_MotorHAT(addr=0x60)
lmotor = mh.getMotor(1)
rmotor = mh.getMotor(2)



# Process the Queue of Motor Speeds
def motorProcess(q):
	while True:
		msg = None
		# Get the most recent message
		while not q.empty():
			msg = q.get(block=True)
		# As long as the motor isn't None.
		if msg is None:
			continue
		if msg == "exit":
			# Quit this function if the message is None
			# This is the indicator to stop this function
			return
		runMotor(lmotor,msg[0])
		runMotor(rmotor,msg[1])


