from CORE.rpistreaml.camera import Camera
from CORE.rpistreaml.streamserver import Server
import cv2

def retrieveImage(cam,imgResize):
    image = cv2.resize(cam.image, (0,0), fx=imgResize, fy=imgResize)
    return image

cam = Camera(mirror=True)
scale=0.5
server = Server(port=5000, promoteErrors = True)
server.serve() # Blocking; waits for a connection before continuing
try:
    try:
        server.startStream(retrieveImage,[cam,scale])
    except Exception as e:
        print e 
except KeyboardInterrupt as e:
    print "exiting"
