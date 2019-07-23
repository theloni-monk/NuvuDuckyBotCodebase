import cv2
import numpy as np
from multiprocessing import Process, Pipe


class Camera:
    def __init__(self, **kwargs):
        self.mirror = kwargs.get("mirror", False)
        self.deviceId=kwargs.get("device", 0)
        self.cam = cv2.VideoCapture(self.deviceId) #captures from the first webcam it sees by default
        
        self.trueRes=(self.cam.get(cv2.CV_CAP_PROP_FRAME_WIDTH),self.cam.get(cv2.CV_VAP_PROP_FRAME_HEIGHT))
        self.scale=(1,1)
        self.outRes=(self.trueRes[0]*self.scale[0],self.trueRes[1]*self.scale[1])

        self.output = None

    def setRes(self,res):
        """Actually just adjust internal scale value"""
        self.scale=(res[0]/self.trueRes[0],res[1]/self.trueRes[1])

    def getFps(self):
        return self.cam.get(cv2.CV_CAP_PROP_FPS)

    @property
    def image(self):
        ret_val, img = self.cam.read()
        if not ret_val:
            raise Exception("Unable to retrieve image from camera")
        if self.mirror:
            img = cv2.flip(img, 1)
        self.output = cv2.resize(img,(0,0),self.scale[0],self.scale[1])

        return self.output

if __name__ == "__main__":
    cam = Camera(mirror=True)
    cv2.imwrite("test/test_image.png", cam.image)
