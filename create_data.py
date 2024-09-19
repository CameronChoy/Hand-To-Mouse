import cv2
import sys
import os
import mediapipe as mp
import numpy as np
import random
import time
random.seed()

CAMERA_FRAME_WIDTH = 1920
CAMERA_FRAME_HEIGHT = 1080
COMPUTE_FRAME_WIDTH = 960
COMPUTE_FRAME_HEIGHT = 540
FPS = 30
FOURCC = cv2.VideoWriter_fourcc(*'MJPG')
DELAY = int(1000/FPS)

timeFormat = "%Y-%m-%d--%H-%M-%S"
# hand_result
# multi_handedness [ classification {index, score, label} ]
# multi_hand_landmarks [ landmark {x, y, z}]
# multi_hand_world_landmarks [ landmark {x, y, z}]

def main():
    if len(sys.argv) != 2:
        print("missing args, needs [gesture_name]")
        exit(1)
    try:
        os.chdir(r'gesture_data')
        if not os.path.isdir(sys.argv[1]): 
            print(f"No folder created, creating new {sys.argv[1]}")
            os.mkdir(sys.argv[1])
        os.chdir(sys.argv[1])            
    except OSError as e:
        print(e)
        exit(1)
    
    if not os.path.isdir('data'):
        os.mkdir('data')

    gesture = sys.argv[1]
    camera = cv2.VideoCapture(0)

    if camera is None or not camera.isOpened(): 
        print("No camera detected, ending process")
        exit(1)
    
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_FRAME_WIDTH)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_FRAME_HEIGHT)
    camera.set(cv2.CAP_PROP_FPS, FPS)
    camera.set(cv2.CAP_PROP_FOURCC, FOURCC)

    drawingModule = mp.solutions.drawing_utils
    handsModule = mp.solutions.hands
    hands = handsModule.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)
    imagenum = 0
    data = []
    while True:
        ret, frame = camera.read()

        hand_result = hands.process(frame)
        
        key = cv2.waitKey(32) & 0xFF
        match key:
            case 113: # q 
                break
            case 32: # spacebar
                
                if hand_result.multi_handedness: # check for hands detected

                    name = f'{gesture}-{imagenum}_{time.strftime(timeFormat)}.jpg' # save image
                    cv2.imwrite(name,frame)
                    print('saving',name)

                    for i, handedness in enumerate(hand_result.multi_handedness): # Save landmarks of every detected hand 
                        hand = 0 if handedness.classification[0].label == "Left" else 1
                        hand_data = [imagenum, hand]
                        
                        for landmark in hand_result.multi_hand_landmarks[i].landmark: # Normalized landmarks
                            hand_data.append(landmark.x)
                            hand_data.append(landmark.y)
                            hand_data.append(landmark.z)
                        for landmark in hand_result.multi_hand_world_landmarks[i].landmark: # World landmarks
                            hand_data.append(landmark.x)
                            hand_data.append(landmark.y)
                            hand_data.append(landmark.z)
                        data.append(hand_data)
                    imagenum += 1
                else:
                    print("No hand detected")
        
        if hand_result.multi_hand_landmarks: # Draw landmarks to video feed
            for landmarks in hand_result.multi_hand_landmarks:
                drawingModule.draw_landmarks(frame, landmarks, handsModule.HAND_CONNECTIONS)
        
        cv2.imshow("camera", cv2.resize(frame, (0, 0), fx = 0.5, fy = 0.5))
    filename = f"data/data_{time.strftime(timeFormat)}.npz"
    np.savez_compressed(filename, data)
    #d = np.load(filename)
    #print(d['arr_0'])
    camera.release()
    cv2.destroyAllWindows()

if __name__ == '__main__': 
    main()