from CORE.rpistreaml.streamclient import Client
import cv2

VERBOSE = True
SERVER_IP = "18.21.190.157"
SERVER_PORT = 5000
client = Client(serverIp="18.21.190.157", port = 5000) # Connects to the server
client.initializeStream()
try:
    try:
        client.startStream()
    except Exception as e:
        print e 

except KeyboardInterrupt as e:
    print "exiting"
    cv2.destroyAllWindows()