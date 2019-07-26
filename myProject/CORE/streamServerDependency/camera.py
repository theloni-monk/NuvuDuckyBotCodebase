import cv2
import numpy as np
from multiprocessing import Process, Pipe


class Camera:
    def __init__(self, **kwargs):
        self.mirror = kwargs.get("mirror", False)
        self.deviceId = kwargs.get("device", 0)
        # captures from the first webcam it sees by default
        self.cam = cv2.VideoCapture(self.deviceId)

        self.trueRes = (int(self.cam.get(cv2.CAP_PROP_FRAME_WIDTH)), int(self.cam.get(
            cv2.CAP_PROP_FRAME_HEIGHT)))  # 3, 4 = CAP_PROP_WIDTH, HEIGHT
        self.sRes = self.trueRes

        self.output = None

    def setRes(self, res):
        """Adjust internal resize resolution"""
        self.sRes = (int(res[0]),int(res[1]))

    def getFps(self):
        return self.cam.get(cv2.CAP_PROP_FPS)  # 5 = CAP_PROP_FPS

    @property
    def image(self):
        ret_val, img = self.cam.read()
        if not ret_val:
            raise Exception("Unable to retrieve image from camera")
        if self.mirror:
            img = cv2.flip(img, 1)
        self.output = cv2.resize(img, self.sRes)

        return self.output


if __name__ == "__main__":
    cam = Camera(mirror=True)
    print cam.trueRes
    cv2.imwrite("test_image.png", cam.image)
