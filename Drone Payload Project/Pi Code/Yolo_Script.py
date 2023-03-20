# -*- coding: utf-8 -*-
"""
Created on Thu Sep 29 09:00:00 2022

@author: Connor
Image Detection with yolov3 and opencv
"""

import cv2
import numpy as np
import time

timeStart = time.time()

#define classes
classNames = ['Closed_valve','Fire_extinguisher','Open_value']

cap = cv2.VideoCapture('1664152920.7081351basicvideo2.avi')
whT = 320

#confidence threshold
confThreshold = 0
#The lower this value the more aggressive it will be at removing boxes
nmsThreshold = 0.3

modelConfiguration = 'yolov3-custom-tiny.cfg'
modelWeights = 'yolov3-custom-tiny_final.weights'

net = cv2.dnn.readNetFromDarknet(modelConfiguration,modelWeights)
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

#function to find the object on the screen
def findObjects(outputs,img):
    hT, wT, cT = img.shape
    #bounding box
    bbox = []
    #class identifier
    classIds = []
    #confidence intervals
    confs = []
    
    for output in outputs:
        for detection in output:
            scores = detection[5:]
            
            classId = np.argmax(scores)
 
            confidence = scores[classId]
            if confidence > confThreshold:
                #print(str(classId) + '  ' + str(confidence))
                #w and h of the bounding box
                w,h = int(detection[2]*wT) , int(detection[3]*hT)
                #x and y are the centrepoint
                x,y = int((detection[0]*wT)-w/2), int((detection[1]*hT)-h/2)
                bbox.append([x,y,w,h])
                classIds.append(classId)
                confs.append(float(confidence))
    #print(len(bbox))
    #output will be the indices of the bounding box to keep
    indices = cv2.dnn.NMSBoxes(bbox,confs,confThreshold,nmsThreshold)
    
    for i in indices:
        box = bbox[i]
        x,y,w,h = box[0],box[1],box[2],box[3]
        cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,255),2)
        cv2.putText(img,f'{classNames[classIds[i]].upper()} {int(confs[i]*100)}%',
                    (x,y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6,(255,0,255),2)

        

running = 1
count = 0
while running:
    #check if image was successfully retrieved
    success, img = cap.read()
    
    #opencv needs the images as blobs, here we convert these to the blob format
    blob = cv2.dnn.blobFromImage(img,1/255,(whT,whT),[0,0,0],1,crop=False)
    net.setInput(blob)
    
    
    layerNames = net.getLayerNames()
    #print(layerNames)
    #0 is not included within the layerNames so this is taken into account with 
    #the -1
    #outputNames = [layerNames[i-1] for i in net.getUnconnectedOutLayers()]
    outputNames = net.getUnconnectedOutLayersNames()
    #print(outputNames)
    #print(net.getUnconnectedOutLayers())
    outputs = net.forward(outputNames)
    #print(outputs[0].shape)
    #print(outputs[1].shape)
    #print(outputs[2].shape)
    #print(outputs[0][0].shape)
    
    findObjects(outputs,img)
    
    #Display image
    cv2.imshow('yolo_script',img)
    cv2.waitKey(1)
    
    
