from rpistream.streamclient import Client
from CORE.parameters import CAM_WIDTH, CAM_HEIGHT
# Import library that allows parallel processing
from multiprocessing import Process, Queue, Value
import time
VERBOSE = True
SERVER_IP = "18.21.90.157"
SERVER_PORT = 5000
WRITE_FILE = False

# TODO: rewrite
# Connects to the server


def connect(client, q, serverIP, serverPort, writeFile, cameraRes):
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
    client = Client(serverIp=SERVER_IP, port=SERVER_PORT, WriteFile=WRITE_FILE,
                    verbose=VERBOSE, imageResolution=(CAM_WIDTH, CAM_HEIGHT))
    # Create a Process for the gamepad, and give it the gamepad queue.
    process = Process(target=connect, args=(
        client, q, SERVER_IP, SERVER_PORT, WRITE_FILE, (CAM_WIDTH, CAM_HEIGHT)))
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
