from rpistream.streamclient import Client
# Import library that allows parallel processing
from multiprocessing import Process, Queue, Value
import time

serverIP = "18.21.90.157"
serverPort = 5000
writeFile = False
cameraRes = (320,240)

#TODO: rewrite
# Connects to the server
def connect(client,q,serverIP,serverPort,writeFile,cameraRes):
	while True:
		# we are now in the loop, check if we should exit
		msg = None
		# Get the most recent message
		while not q.empty():
			msg = q.get(block=False)
		# Check if the message is None or "exit"
		if msg is None:
			pass
		elif msg == 'exit':
			return
		# connect to a client
		try:
			client.connect()
			print("Connected")
			client.startStream()
		except Exception as e:
			print(e)

if __name__ == '__main__':
	q = Queue()
	client = Client(serverIp=serverIP, port=serverPort, WriteFile=writeFile, verbose=False, imageResolution=cameraRes)
	# Create a Process for the gamepad, and give it the gamepad queue.
	process = Process(target=connect, args=(client,q,serverIP,serverPort,writeFile,cameraRes))
	# Start the gamepadProcess
	process.start()
	# Prevent this main process from terminating until ESCAPE is pressed
	try:
		while True:
			time.sleep(1)
	except KeyboardInterrupt:
		pass
	q.put('exit')
	if not client is None:
		client.close()
	process.join()
