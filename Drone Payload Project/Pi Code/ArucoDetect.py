# -*- coding: utf-8 -*-
"""
Created on Thu Sep 29 09:00:00 2022

@author: Alex, Connor
Image Detection with yolov3 and opencv
"""

import numpy as np
import cv2
import sys
#from utils import aruco_display
#from utils import ARUCO_DICT
import argparse
import time



matrix_coefficients = np.load("calibration_matrix.npy")
distortion_coefficients = np.load("distortion_coefficients.npy")
aruco_dict_type = cv2.aruco.DICT_5X5_100
cv2.aruco_dict = cv2.aruco.Dictionary_get(aruco_dict_type)


class Aruco:
    def __init__(self):
        self.timeStart = time.time()
        self.xyz = "Unknown"
        self.distance = 10000

    def start(self):
        return 

    def update(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        parameters = cv2.aruco.DetectorParameters_create()
        self.corners, self.ids, rejected_img_points = cv2.aruco.detectMarkers(gray, cv2.aruco_dict,parameters=parameters,
        cameraMatrix=matrix_coefficients,
        distCoeff=distortion_coefficients)
       

    def draw(self, frame):
        # If markers are detected
        corners = self.corners
        ids = self.ids
        if len(corners) > 0:
            for i in range(0, len(ids)):
                # Estimate pose of each marker and return the values rvec and tvec---(different from those of camera coefficients)
                rvec, tvec, markerPoints = cv2.aruco.estimatePoseSingleMarkers(corners[i], 0.0225 * 2, matrix_coefficients,
                                                                        distortion_coefficients)

                self.xyz = f"X:{str(round(tvec[0][0][0],3))},Y:{str(round(tvec[0][0][1],3))},Z:{str(round(tvec[0][0][2],3))}"
                self.distance = round(tvec[0][0][2],3)

                # Draw a square around the markers

                #print("---------Rvec----------")
                #print(rvec)
                #print("-----------------------")
                #print("\n")
                #print("---------Tvec----------")
                #print(tvec)
                #print("-----------------------")

                cv2.aruco.drawDetectedMarkers(frame, corners) 


                for (markerCorner, markerID) in zip(corners, ids):
                    # extract the marker corners (which are always returned in
                    # top-left, top-right, bottom-right, and bottom-left order)
                    corners = markerCorner.reshape((4, 2))
                    (topLeft, topRight, bottomRight, bottomLeft) = corners
                    # convert each of the (x, y)-coordinate pairs to integers
                    topRight = (int(topRight[0]), int(topRight[1]))
                    bottomRight = (int(bottomRight[0]), int(bottomRight[1]))
                    bottomLeft = (int(bottomLeft[0]), int(bottomLeft[1]))
                    topLeft = (int(topLeft[0]), int(topLeft[1]))

                    #cv2.line(frame, topLeft, topRight, (0, 255, 0), 2)
                    #cv2.line(frame, topRight, bottomRight, (0, 255, 0), 2)
                    #cv2.line(frame, bottomRight, bottomLeft, (0, 255, 0), 2)
                    #cv2.line(frame, bottomLeft, topLeft, (0, 255, 0), 2)
                    # compute and draw the center (x, y)-coordinates of the ArUco
                    # marker
                    cX = int((topLeft[0] + bottomRight[0]) / 2.0)
                    cY = int((topLeft[1] + bottomRight[1]) / 2.0)
                    cv2.circle(frame, (cX, cY), 4, (0, 0, 255), -1)
                    # draw the ArUco marker ID on the image
                    cv2.putText(frame, str(markerID),(topLeft[0], topLeft[1] - 10), cv2.FONT_HERSHEY_SIMPLEX,
                        0.5, (0, 255, 0), 2)

                    cv2.putText(frame,str(round(tvec[0][0][0],3)) + " " + str(round(tvec[0][0][1],3)) + 
                    " " + str(round(tvec[0][0][2],3)),(bottomRight[0], bottomRight[1] - 10), cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, (0, 255, 0), 2)
                    
                    #print("[Inference] ArUco marker ID: {}".format(markerID))
                    # show the output image

                # Draw Axis
                cv2.aruco.drawAxis(frame, matrix_coefficients, distortion_coefficients, rvec, tvec, 0.01)
                
        self.frame = frame

        


