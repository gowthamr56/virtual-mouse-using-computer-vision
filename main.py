import cv2
import mediapipe as mp
import numpy as np
import autopy
import time
import HandTrackingModule as htm
import pyautogui

#########################################
wCam, hCam = 640, 480
wScreen, hScreen = autopy.screen.size()
frameR = 100  # Frame Reduction
smoothening = 10
previousLocationX, previousLocationY = 0, 0
currentLocationX, currentLocationY = 0, 0
currentTime, previousTime = 0, 0
#########################################

capture = cv2.VideoCapture(0)
capture.set(3, wCam)
capture.set(4, hCam)

detector = htm.handDetector(maxHands=1)

while capture.isOpened():

    success, img = capture.read()

    # steps
    # 1. find hand landmarks
    img = detector.findHands(img)
    lmList, boundingBox = detector.findPosition(img)

    # 2. get the tip of the index & middle fingers
    if lmList:
        x1, y1 = lmList[8][1:]
        x2, y2 = lmList[12][1:]
        '''print(x1, y1, x2, y2)'''

        # 3. check which fingers are up
        fingers = detector.fingersUp()
        '''print(fingers)'''

        '''
        cv2.rectangle(img, (frameR, frameR), (wCam-frameR, hCam-frameR), (0, 0, 255), 2)
        '''

        # 4. only index finger : moving mode
        if fingers[1] == 1 and fingers[2] == 0:            
            # 5. convert coordinates
            x3 = int(np.interp(x1, (0, wCam), (0, wScreen)))
            y3 = int(np.interp(y1, (0, hCam), (0, hScreen)))    
            '''
            x3 = int(np.interp(x1, (frameR, wCam), (0, wScreen)))
            y3 = int(np.interp(y1, (frameR, hCam), (0, hScreen)))    
            '''

            # 6. smoothen values
            currentLocationX = previousLocationX + (x3 - previousLocationX) / smoothening
            currentLocationY = previousLocationY + (x3 - previousLocationY) / smoothening
            
            # 7. move mouse
            autopy.mouse.move(wScreen-x3, y3)
            cv2.circle(img, (x1, y1), 12, (255, 0, 255), cv2.FILLED)
            previousLocationX, previousLocationY = currentLocationX, currentLocationY

        # 8. both index & middle fingers are up : clicking mode
        if fingers[1] == 1 and fingers[2] == 1:
            # 9. find distance between the fingers
            length, img, lineInfo = detector.findDistance(8, 12, img)
            '''print(length)'''
            if length < 30:
                cv2.circle(img, (lineInfo[4], lineInfo[5]), 12, (0, 255, 0), cv2.FILLED)
                # 10. click mouse if distance short
                autopy.mouse.click()

        # 11. both thumb and index fingers are up : right click mode
        if fingers[0] == 1 and fingers[1] == 1:
            # 12. find distance between the fingers
            length, img, lineInfo = detector.findDistance(4, 8, img)
            '''print(length)'''
            if length < 30:
                cv2.circle(img, (lineInfo[4], lineInfo[5]), 12, (0, 255, 0), cv2.FILLED)
                # 13. perform right click if distance short
                pyautogui.click(button='right', clicks=1)

    # frame per second
    currentTime = time.time()
    fps = 1 / (currentTime-previousTime)
    previousTime = currentTime

    cv2.putText(img, f"FPS:{int(fps)}", (20, 50), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)

    cv2.imshow('AI Virtual Mouse', img)
    key = cv2.waitKey(1)
    if key == 13:
        break
    