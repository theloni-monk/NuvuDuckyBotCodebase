import socket
import numpy as np
import io
import cv2
import zstandard 
import atexit
from netutils import *
import sys
import platform




class Client:
    def __init__(self, **kwargs):
        #self.os=platform.system()
        self.verbose = kwargs.get("verbose", False)
        self.promoteErrors=kwargs.get("promoteErrors", False)
        # output file seems to be corrupted: likely due to output file stream not being closed correctly
        self.Write = kwargs.get("writeFile", False)
        if platform.system() == 'Windows':
            self.writepath = kwargs.get("path", ".\\")
        else:
            self.writepath = kwargs.get("path", "./")
        self.FileFPS = kwargs.get("fileoutFps", 10)
        self.FileName = kwargs.get("fileName", 'outpy')
        self.iRes = kwargs.get("imageResolution", (320, 240))
        fourcc = None
        self.out = None
        if self.Write:
            try:
                fourcc = cv2.cv.CV_FOURCC(*'MJPG') # OpenCV 2 function
            except:
                #fourcc = cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')  # OpenCV 3 function
                fourcc = cv2.VideoWriter_fourcc(*'MJPG')
            
            self.out = cv2.VideoWriter(
                self.writepath+self.FileName+'.avi', fourcc, self.FileFPS, self.iRes)
        
        #self.windowRes = (640, 480)
        self.windowTitle=kwargs.get("Title","Feed")
        self.prevFrame = 0

        # creates socket
        self.log("Initializing socket...")
        self.ip = kwargs.get("serverIp", "localhost")
        self.s = socket.socket()
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # connects via socket to server at provided ip over the provided port
        self.log("Connecting...")
        # connect over port
        self.s.connect((self.ip, kwargs.get("port", 8080)))

        # instanciate a decompressor which we can use to decompress our frames
        self.D = zstandard.ZstdDecompressor()
        # the scaling factor for the display
        self.viewScale = kwargs.get("viewScale", 1)

        # when the user exits or the stream crashes it closes so there arn't orfaned processes
        atexit.register(self.close)

        self.frameno=None
        self.log("Ready")

    def log(self, m):
        """prints out if verbose"""
        if self.verbose:
            print(m)  # printout if server is in verbose mode

    def recv(self, size=1024):
        """Recieves a single frame
        Args:
            size: how big a frame should be
                default: 1024
        returns:
            single data frame
        """
        data = bytearray()
        while 1:
            buffer = self.s.recv(1024)
            data += buffer
            if len(buffer) == 1024:
                pass
            else:
                return data

    def initializeStream(self):
        """Recvs initial frame and preps"""
        # initial frame cant use intra-frame compression
        initMsg = recv_msg(self.s)
        print "recieved initial frame"
        self.prevFrame = np.load(io.BytesIO(
            self.D.decompress(initMsg)))
        self.frameno = 0
        self.log("stream initialized")

    def decodeFrame(self):
        """Decodes single frame of data from an initialized stream"""
        try:
            r = recv_msg(self.s)  # gets the frame difference
        except socket.error as e:
            self.close(e) #catch socket error

        try:
            if len(r) == 0:
                pass
        except TypeError as e:
            self.close(ValueError("Server sent Null data"))


        # load decompressed image
                # np.load creates an array from the serialized data
        img = (np.load(io.BytesIO(self.D.decompress(r)))  # decompress the incoming frame difference
                + self.prevFrame).astype("uint8")  # add the difference to the previous frame and convert to uint8 for safety

        self.log("recieved {}KB (frame {})".format(int(len(r)/1000), self.frameno))  # debugging
        self.frameno+=1

        self.prevFrame = img  # save the frame

        if self.Write:
            try:
                self.out.write(img)  # save frame to a video file client side
            except Exception as e:
                self.close(e)

        return img

    def startStream(self):
        """Decodes files from stream and displays them"""  
        #if self.prevFrame == 0:
        #    self.initializeStream() #decode initial frame 
        cv2.namedWindow(self.windowTitle, cv2.WINDOW_NORMAL)

        while True:
            img=self.decodeFrame() #decode frame
            
            # adjust core resolution: 
            # note: there isn't really a reason for viewScale to ever not be one
            img=cv2.resize(img, (0, 0), fx=self.viewScale, fy=self.viewScale)
            #dynamically scale image size to window size
            cv2.imshow(self.windowTitle, img) #cv2.resize(img, (0, 0), fx=self.windowRes[0]/img.shape[0], fy=self.windowRes[1]/img.shape[1]))

            if cv2.waitKey(1) == 27:
                self.close()
                break  # esc to quit

    def close(self, E=None):
        """Closes socket and opencv instances"""
        if self.Write:
            self.out.release()
        self.s.close()
        if(E!=None):
            if self.promoteErrors:
                self.log("Stream raised error: " + str(E))
                raise E
            else:
                print("Stream closed on Error\n" + str(E))
        else:
            self.log("Stream closed")
        
        try:
            cv2.destroyAllWindows()
        except Exception:
            pass

        #if not self.promoteErrors:
        #    self.log("Stream encountered error without being set to promote it")
        #    sys.exit(0)


# if you directly run this file it will act run this
if __name__ == "__main__":
    client = Client(serverIp="localhost", port=5000)
    client.startStream()
