from CORE.rpistreaml.streamclient import Client
import cv2

SERVER_IP = "localhost"
SERVER_PORT = 5000
#NOTE: if you change the resolution in the server, you have to change it in the client
client = Client(serverIp=SERVER_IP, port = SERVER_PORT, promoteErrors = True, writeFile = True) # Connects to the server
client.initializeStream()
try:
    try:
        client.startStream()
    except Exception as e:
        print e 
except KeyboardInterrupt as e:
    print "exiting"
    cv2.destroyAllWindows()
