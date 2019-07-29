import sys
sys.path.append("..")
import cv2
from CORE.streamServerDependency.camera import Camera

c = Camera()
cv2.namedWindow("test")
while True:
    cv2.imshow("test", c.image)
    cv2.waitKey(1)