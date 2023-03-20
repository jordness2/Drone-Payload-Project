# -*- coding: utf-8 -*-
"""
Created on Thu Sep 29 09:00:00 2022

@author: Connor
Image Detection with yolov3 and opencv
"""

import cv2
import numpy as np
import time

import cv2 as cv
from PIL import Image
import ST7735 as ST7735

disp = ST7735.ST7735(
port =0 ,
cs= ST7735.BG_SPI_CS_FRONT , # BG_SPI_CSB_BACK or BG_SPI_CS_FRONT
dc=9 ,
backlight =19 , # 18 for back BG slot , 19 for front BG slot .
rotation =90 ,
spi_speed_hz = 4000000
)
WIDTH = disp.width
HEIGHT = disp.height
# Initialize display .
disp.begin()


#define classes
classNames = ['Closed_valve','Fire_extinguisher','Open_value']

#cap = cv2.VideoCapture('1664152920.7081351basicvideo2.avi')
cap = cv2.VideoCapture(0)

whT = 320

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 320)

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
    wah = False

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
                wah = True
                print(str(classId) + '  ' + str(confidence))
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

    return wah

        

running = 1
count = 0
i = 1

# used to record the time when we processed last frame
prev_frame_time = 0
 
# used to record the time at which we processed current frame
new_frame_time = 0

while running:
    start = time.time()
    #check if image was successfully retrieved
    success, img = cap.read()
    new_frame_time = time.time()
    
    #opencv needs the images as blobs, here we convert these to the blob format
    blob = cv2.dnn.blobFromImage(img,1/255,(whT,whT),[0,0,0],1,crop=False)
    net.setInput(blob)
    
    
    layerNames = net.getLayerNames()
    #print(layerNames)
    #0 is not included within the layerNames so this is taken into account with 
    #the -1
    outputNames = [layerNames[i-1] for i in net.getUnconnectedOutLayers()]
    #outputNames = net.getUnconnectedOutLayersNames()
    #print(outputNames)
    #print(net.getUnconnectedOutLayers())
    outputs = net.forward(outputNames)
    #print(outputs[0].shape)
    #print(outputs[1].shape)
    #print(outputs[2].shape)
    #print(outputs[0][0].shape)
    
    findObjects(outputs,img)
    
    #if(wah):
    #    cv2.imwrite('Found Frame Image - ' + str(start) + '.jpg', img)

    #Display image

    im_pil = Image.fromarray( img )
    # Display the resulting frame
    # Resize the image
    im_pil = im_pil.resize(( WIDTH , HEIGHT ) )
    # display image on lcd
    disp.display( im_pil )
    #cv. imshow(' frame ', gray )
    if cv.waitKey( 1 ) == ord( 'q'):
        break

    #cv2.imshow('yolo_script',img)
    #cv2.waitKey(1)

    end = time.time()
    print(f"[Iteration {i}]: {end-start}/")
    fps = 1/(new_frame_time-prev_frame_time)
    prev_frame_time = new_frame_time
    #print("Estimated frames per second : {0}".format(fps))


    i = i + 1
    
cap.release()