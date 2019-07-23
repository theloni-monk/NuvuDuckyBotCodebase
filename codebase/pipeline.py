# THINGS YOU SHOULD DO:
# 1. Write all the code to convert images into motor outputs into one function called 'pipeline'
# 2. Ensure the pipeline function takes BOTH the image and motorq as inputs and outputs to the motorq.

import numpy as np
import cv2
from multiprocessing import Queue
def pipeline(image, motorq):
    imageOut = image
    pass # replace with your code
    return imageOut # to help debug your code, we recommend you mark up the given image and return it here to see it over the stream

# you will likely needs to separate your code into various functions called within pipeline
#EX: def findlines(imgIn): 
#       imgOut = houghLines(cannyEdge(imgIn,[params]))
#       return imgOut