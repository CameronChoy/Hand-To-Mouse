import cv2
import sys
import os
import mediapipe as mp
import random
random.seed()

def main():
    if len(sys.argv) != 2:
        print("missing args, needs [gesture_name]")
        exit(1)
    try:
        os.chdir(r'D:\VisionProject\gesture_data')
        os.chdir(sys.argv[1])
    except OSError as e:
        print(e)
        exit(1)
    
    gesture = sys.argv[1]
    camera = cv2.VideoCapture(0)
    if camera is None or not camera.isOpened(): 
        print("No camera detected, ending process")
        exit(1)
    
    drawingModule = mp.solutions.drawing_utils
    handsModule = mp.solutions.hands
    hands = handsModule.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)
    
    while True:
        ret, frame = camera.read()
        image = frame.copy()

        hand_result = hands.process(frame)
        if hand_result.multi_hand_landmarks:
            for landmarks in hand_result.multi_hand_landmarks:
                drawingModule.draw_landmarks(image, landmarks, handsModule.HAND_CONNECTIONS)
        
        cv2.imshow("camera", image)
        key = cv2.waitKey(32) & 0xFF
        match key:
            case 113: # q 
                break
            case 32: # spacebar
                name = f'{gesture}_id{str(random.randrange(1000, 999999, 1))}.jpg'
                cv2.imwrite(name,frame)
                print('saving')
    camera.release()
    cv2.destroyAllWindows()

if __name__ == '__main__': 
    main()