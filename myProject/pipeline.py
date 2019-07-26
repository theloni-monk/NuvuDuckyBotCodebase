# THINGS YOU SHOULD DO:
# 1. Write all the code to convert images into motor outputs into one function called 'pipeline'
# 2. Ensure the pipeline function takes BOTH the image and motorq as inputs and outputs to the motorq.

import numpy as np
import cv2
import math
from multiprocessing import Queue
def region_of_interest(img, vertices):
    mask = np.zeros_like(img)
    match_mask_color = 255
    cv2.fillPoly(mask, vertices, match_mask_color)
    masked_image = cv2.bitwise_and(img, mask)
    return masked_image

def draw_lines(img, lines, color=[255, 0, 0], thickness=3):
    line_img = np.zeros(
        (
            img.shape[0],
            img.shape[1],
            3
        ),
        dtype=np.uint8
    )
    img = np.copy(img)
    if lines is None:
        return

    for line in lines:
        for x1, y1, x2, y2 in line:
            cv2.line(line_img, (x1, y1), (x2, y2), color, thickness)

    img = cv2.addWeighted(img, 0.8, line_img, 1.0, 0.0)

    return img

def pipeline(image, motorq):

    #imageOut = cv2.GaussianBlur(image,(3,3),0)

    #pass # replace with your code

    #return imageOut # to help debug your code, we recommend you mark up the given image and return it here to see it over the stream
    
    
    height = image.shape[0]
    width = image.shape[1]
    region_of_interest_vertices = [
        (0, height),
        (width * 0.2, height / 2),
        (width , height / 2),
        (width , height),
        ]
    #blur_image = cv2.bilateralFilter(image,9,75,75)
    blur_image = cv2.medianBlur(image,5)

    gray_image = cv2.cvtColor(blur_image, cv2.COLOR_RGB2GRAY)

    cannyed_image = cv2.Canny(gray_image, 100, 200)

    cropped_image = region_of_interest(
        cannyed_image,
        np.array(
            [region_of_interest_vertices],
            np.int32
        ),
    )

    lines = cv2.HoughLinesP(
        cropped_image,
        rho=6,
        theta=np.pi / 60,
        threshold=160,
        lines=np.array([]),
        minLineLength=40,
        maxLineGap=25
    )
 
    left_line_x = []
    left_line_y = []
    right_line_x = []
    right_line_y = []

    leftFound = False
    rightFound = False

    if np.all(lines) != None and not np.any(lines) == None: 
        for line in lines:
            for x1, y1, x2, y2 in line:
                slope = float(y2 - y1) / (x2 - x1)
                if math.fabs(slope) < 0.5:
                    continue
                if slope <= 0:
                    left_line_x.extend([x1, x2])
                    left_line_y.extend([y1, y2])
                else:
                    right_line_x.extend([x1, x2])
                    right_line_y.extend([y1, y2])

        min_y = int(image.shape[0] * (3.0 / 5.0))
        max_y = int(image.shape[0])


    try:
        poly_left = np.poly1d(np.polyfit(
            left_line_y,
            left_line_x,
            deg=1
        ))
        
        left_x_start = int(poly_left(max_y))
        left_x_end = int(poly_left(min_y))
        leftFound = True
    except:
        leftFound = False
    
    try:
        poly_right = np.poly1d(np.polyfit(
            right_line_y,
            right_line_x,
            deg=1
        ))
        
        right_x_start = int(poly_right(max_y))
        right_x_end = int(poly_right(min_y))
        rightFound = True
    except:
        leftFound = False

    if leftFound:
        line_image = draw_lines(
            image,
            [[
                [left_x_start, max_y, left_x_end, min_y],
                [right_x_start, max_y, right_x_end, min_y],
            ]],
            thickness=5,
        )

    if rightFound:
        line_image = draw_lines(
            image,
            [[
                [right_x_start, max_y, right_x_end, min_y],
            ]],
            thickness=5,
        )
    elif (not leftFound) and (not rightFound):
        line_image = image


    return line_image
# you will likely needs to separate your code into various functions called within pipeline
#EX: def findlines(imgIn): 
#       imgOut = houghLines(cannyEdge(imgIn,[params]))
#       return imgOut
