import numpy as np
import cv2
import serial
import pygame
from pygame.locals import *
from pygame import *
import time 


import urllib.request


url = 'http://192.168.43.1:8080/shot.jpg'
trafficlight = cv2.CascadeClassifier('traffic_light.xml')
stop = cv2.CascadeClassifier('stop_sign.xml')
#cap = cv2.VideoCapture(0)
#minimum value to proceed traffic light state validation
threshold = 150 


class RCTest(object):

    def __init__(self):


        pygame.init()
        screen = display.set_mode((640,480))
        display.set_caption('the input..')
        self.ser = serial.Serial('COM35', 115200, timeout=1)
        self.send_inst = True
        self.steer()

    def stop(self):
          print("Danger ......stop")
          self.ser.write(chr(0).encode())
          

    def forward(self):
          print("Safe go forward...")
          self.ser.write(chr(1).encode())
          

    def steer(self):

        while self.send_inst:
            imgResp=urllib.request.urlopen(url)
            imgNp=np.array(bytearray(imgResp.read()),dtype=np.uint8)
            img=cv2.imdecode(imgNp,-1)
            cv2.imshow('test',img)

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            frame = trafficlight.detectMultiScale(gray, scaleFactor=1.1,
                    minNeighbors=5,
                    minSize=(30, 30),
                    flags=cv2.CASCADE_SCALE_IMAGE )
            stopsign = stop.detectMultiScale(gray, scaleFactor=1.1,
                       minNeighbors=5,
                       minSize=(30, 30),
                       flags=cv2.CASCADE_SCALE_IMAGE )

            if not any(map(len, frame)):
                print("leist emyg")
                self.forward()

            for (sx,sy,sw,sh) in stopsign:
                cv2.rectangle(img,(sx,sy),(sx+sw,sy+sh),(255,255,255),2)
                print("Stop sign")
                cv2.putText(img, 'Stop signal Ahead...pls stop', (5, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,69,255), 2)
                self.stop()              
                time.sleep(0.2)
                self.stop()
                
            for (x,y,w,h) in frame:
                cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,255),2)
                #roi_gray = gray[y:y+h, x:x+w]
                #roi_color = img[y:y+h, x:x+w]
                #self.stop()
                #self.ser.write(chr(0).encode())
                roi = gray[y+10:y + h-10, x+10:x + w-10]
                mask = cv2.GaussianBlur(roi, (25, 25), 0)
                (minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(mask)
                # check if light is on
                if maxVal - minVal > threshold:
                    cv2.circle(roi, maxLoc, 5, (255, 0, 0), 2)
                    
                # Red light
                    if 1.0/8*(h-30) < maxLoc[1] < 4.0/8*(h-30):
                        cv2.putText(img, 'Red', (x+5, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                        cv2.putText(img, 'Red Signal--Pls follow Traffic rules..', (5, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 2)
                        print("red")  
                        self.stop()
                    
                    # Green light
                    elif 5.5/8*(h-30) < maxLoc[1] < h-30:
                        cv2.putText(img, 'Green', (x+5, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                        cv2.putText(img, 'Move on -- have a safe journey ', (5, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)
                        print("green")
                        #self.green_light = True
                        self.forward()

            
            cv2.imshow('test',img)
            if ord('q')==cv2.waitKey(10):
                self.stop()
                print ('Exit')
                self.send_inst = False
                self.ser.close()
                exit(0)




if __name__ == '__main__':
    RCTest()
