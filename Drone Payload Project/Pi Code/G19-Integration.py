from re import L
import numpy as np
import sys
import cv2
import time
import math
import VideoStreamOverride
import AirQuality
import YoloModel
import ArucoDetect
import requests
import base64
from datetime import datetime
from time import sleep
from IP_Temp_Img import lcd_text_dis, get_ip
import servov2

import cv2 as cv
from PIL import Image
import ST7735 as ST7735

url = 'http://172.19.52.193:5001'
Imgurl = url+'/taip/taip'
AQurl = url+'/aqs/aqs'
Deployurl = url+'/st/deployButton'
Deployurl2 = url+'/st/getDeployFlag'


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







HRes = 320
VRes = 320

UseModel = True
UseAruco = True
UseAQ = True
UseServer = True

src = '1664152920.7081351basicvideo2.avi'

if(UseAQ):
        AQSubsystem = AirQuality.AirQualitySensor()
Vision = VideoStreamOverride.VideoStream((HRes,VRes),framerate=30,UseModel=UseModel,UseAruco=UseAruco)
Model = YoloModel.Yolo()
Aruco = ArucoDetect.Aruco()
Servo = servov2.servo()


class Payload:
        def __init__(self):
                self.test = None
                self.temperature = None   
                self.Deploy = False
                self.SendDeploy = False
                self.CanDeploy = False
                self.OnceDeploy = True
                self.Distances = [1000,1000,1000,1000]

        def start(self):
                print("Starting Payload")
                try:
                        Vision.start()
                        if(UseAQ):
                                AQSubsystem.start()
                        time.sleep(1)
                        aa = 1
                        # used to record the time when we processed last frame
                        prev_frame_time = 0
                        
                        # used to record the time at which we processed current frame
                        new_frame_time = 0

                                                
                        delay = 0.5  # Debounce the proximity tap
                        mode = 0     # The starting mode
                        last_page = 0
                        light = 1

                        image_timer = time.time()
                        aqs_timer = time.time()

                        while(1):
                                #start = time.time()
                                new_frame_time = time.time()
                                #self.temperature, self.Pressure = self.get_parameters()
                                #print("a")
                                frame, grabbed = Vision.read()
                                if(not frame.any()):
                                        continue
                                
                                #print("b")

                                name = "default"
                                xyz = "Unknown"

                                if(UseAruco):
                                        Aruco.update(frame)
                                        
                                if(UseModel and Aruco.ids is None):
                                        try:
                                                Model.update(frame)
                                                if(Model.targetConfidence > 0):
                                                        name = f"{Model.target}"
                                        except:
                                                print("Model Failed")

                                if(UseAruco):

                                        try:
                                                Aruco.draw(frame)
                                                if Aruco.ids is not None:
                                                        if(time.time()-image_timer > 1):
                                                                name = f"Aruco: {Aruco.ids[0]}"
                                                                image_timer = time.time()
                                                        
                                                        #print(name)
                                                        xyz = Aruco.xyz

                                                        average = sum(self.Distances)/len(self.Distances)

                                                        if((Aruco.distance > 0.2 and average > 50) or (average < 50)) and 45 in Aruco.ids[0]:
                                                                self.Distances.append(Aruco.distance)
                                                                self.Distances.remove(self.Distances[0])

                                                        average = sum(self.Distances)/len(self.Distances)
                                                        print(f'{average}  -  {Aruco.distance}')

                                                        if(average < 0.6 and not self.Deploy and 45 in Aruco.ids[0]):
                                                                self.Deploy = True
                                                                self.SendDeploy = True

                                        except:
                                                print("Couldn't Draw ArUco")
                                        

                                
                                #if(aa % 10 == 0):
                                #        name = str(aa)

                                try:
                                        if(UseServer):
                                                self.sendImage(frame,name,xyz)
                                except:
                                        print("Couldn't send image")

                                if(UseAQ):
                                        AQSubsystem.update()

                                if((time.time() - aqs_timer > 5) and UseAQ and UseServer):
                                        aqs_timer = time.time()
                                        try:
                                                #print("ping aqs")
                                                r = requests.post(url = AQurl, json={"data": AQSubsystem.to_json()})
                                        except:
                                                print("Couldn't ping AQS")
                                


                                if(UseAQ):
                                        if AQSubsystem.proximity > 1500 and time.time() - last_page > delay:
                                                print("Change")
                                                mode = (mode + 1) % 3

                                last_page = time.time()

                                if mode == 0:
                                        #print(get_ip())
                                        lcd_text_dis(get_ip())

                                if mode == 1:
                                        #print(temp())
                                        lcd_text_dis(str(round(AQSubsystem.temperature,3)) + " C")

                                if mode == 2:
                                # This is the image display
                                        #Display image
                                        #cv2.imshow('WebcamVideo',frame)
                                        #cv2.waitKey(1)
                                        im_pil = Image.fromarray( frame )
                                        # Display the resulting frame
                                        # Resize the image
                                        im_pil = im_pil.resize(( WIDTH , HEIGHT ) )
                                        # display image on lcd
                                        disp.display( im_pil )
                                        
                                        #cv. imshow(' frame ', gray )
                                        #if cv.waitKey( 1 ) == ord( 'q'):
                                        #        break

                                if(self.Deploy and self.SendDeploy and UseServer):
                                        try:
                                                r = requests.post(Deployurl, {"deploy": True})
                                                if(r.status_code == 201):
                                                        self.SendDeploy = False
                                                        print("Enabled Button")
                                        except:
                                                print("Deploy Post Failed")
                                if(self.Deploy and not self.SendDeploy and UseServer):
                                        try:
                                                getr = requests.get(Deployurl2)
                                                if getr.json()[0]['deployFlag']:
                                                        self.CanDeploy = True
                                                        self.Deploy = False
                                                        print("Button Pressed")
                                        except:
                                                print("Get Request Failed")

                                if(self.CanDeploy and self.OnceDeploy):
                                        print("Deploying")
                                        #time.sleep(5)
                                        Servo.start()
                                        print("Moving Down")
                                        Servo.motor_change(1)
                                        print("Moving Up")
                                        Servo.motor_change(-1)
                                        print("Stopping Motor")
                                        Servo.motor_change(0)
                                        Servo.cleanUp()
                                        self.CanDeploy = False
                                        self.OnceDeploy = False



                                        

                                #end = time.time()
                                #print(f"[Iteration {aa}]: {end-start}/")
                                fps = 1/(new_frame_time-prev_frame_time)
                                prev_frame_time = new_frame_time
                                print("Estimated frames per second : {0}".format(fps))

                                aa = aa + 1

                                #Display image
                                #cv2.imshow('WebcamVideoa',frame)
                                #cv2.waitKey(1)
                                #DrawnFrame = Vision.read()
                                #AQSubsystem.Display(DrawnFrame)
                except:
                        print("Unexpected error:", sys.exc_info())
                        cv2.destroyAllWindows()
                        self.stop()
       
#=================== HELPER FUNCTIONS ========================================
        #stop : Closes the application gracefully
        def stop(self):
                print("stop 1")
                Vision.stop()
                cv2.destroyAllWindows()
                return

        def sendImage(self, image, name="default", xyz = "Unknown"):
                retval, buffer = cv2.imencode('.jpeg', image)
                jpg_as_text = base64.b64encode(buffer)
                base64img = {"data": jpg_as_text, "name" : name, "xyz": xyz, "time":datetime.now().strftime("%H:%M:%S")}
                r = requests.post(Imgurl, data=base64img)
                return r

#=================== MAIN PROGRAM EXECUTION ==================================


time.sleep(2.0)
robot = Payload()
robot.start()
print("sleep for 3")
time.sleep(3.0)
print("3 is up")
robot.stop()
