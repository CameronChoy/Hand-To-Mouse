import sys
import time
import numpy as np
from pathlib import Path
import json
from argparse import ArgumentParser, BooleanOptionalAction
from client import Client, MsgType, MouseStatus
import mediapipe as mp
import cv2
import torch
from torch import load, argmax, tensor, float32
import cursor
import model
from model import gr_torch_model
#from keras.models import load_model

# Gesture Recognizer:
# result.gestures = [[Category(index, score, display_name, categgory_name),...]]
# handedness = [[Category(index,score,display_name,category_name),...]]
# result.hand_landmarks = [[NormalizedLandmark(x,y,z),...]]
# result.hand_world_landmarks = [[Landmark(x,y,z),...]]
# 
# Multi Hand Landmark:
# result.multi_hand_landmarks = [landmark(x,y,z),...]
# result.multi_hand_world_landmarks
# result.multi_handedness
CAMERA_FRAME_WIDTH = 1920
CAMERA_FRAME_HEIGHT = 1080
COMPUTE_FRAME_WIDTH = 960
COMPUTE_FRAME_HEIGHT = 540
FPS = 30
FOURCC = cv2.VideoWriter_fourcc(*'MJPG')
DELAY = int(1000/FPS)

class HandStatus:
    def __init__(self):
        self.lmouse = False
        self.rmouse = False
        self.scroll_up = False
        self.scroll_down = False

# Marks plane in user's space with rect (size defined by user's hands) that represents the whole screen
# hand coordinates will be projected onto plane to find position relative to rect to calculate mouse position
def configure_hand_space(lhand, rhand):
    pass

def startRecognizer(model_path : Path, video_index : int, device : torch.device):
    
    camera = cv2.VideoCapture(video_index)
    if camera is None or not camera.isOpened(): 
        print("No camera detected, ending process")
        return

    try:
        gesture_model = load(f"{model_path}/model.pt", weights_only=False).to(device)#load_model(model_path)
        gesture_model.eval()
        with open(f"{model_path}/config.json") as f:
            config = json.load(f)
        print(config['gesture_count'], type(config['gesture_count']))
    except IOError as e:
        print(e)
        print("Model path needs to link to directory.")
        return
    
    #client = Client(('localhost',port))
    
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_FRAME_WIDTH)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_FRAME_HEIGHT)
    camera.set(cv2.CAP_PROP_FPS, FPS)
    camera.set(cv2.CAP_PROP_FOURCC, FOURCC)
    '''
    BaseOptions = mp.tasks.BaseOptions
    GestureRecognizer = mp.tasks.vision.GestureRecognizer
    GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions
    VisionRunningMode = mp.tasks.vision.RunningMode
    '''
    drawingModule = mp.solutions.drawing_utils
    handsModule = mp.solutions.hands

    
    
    '''
    options = GestureRecognizerOptions(
        base_options=BaseOptions(model_asset_path="gesture_recognizer.task"),
        running_mode=VisionRunningMode.VIDEO, num_hands=2)

    recognizer = GestureRecognizer.create_from_options(options)
    '''
    hands = handsModule.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)

    previous = MouseStatus.IDLE

    timestamp = 0
    while True:
        delta = time.time() * 1000 # amount of time in miliseconds to delay next loop
        ret, frame = camera.read()
        
        '''
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
        
        result = recognizer.recognize_for_video(mp_image, timestamp)
        for idx, landmarks in enumerate(result.hand_landmarks):
            coords = landmarks[0]
            gesture = result.gestures[idx][0].category_name

            center = (int(coords.x * frame.shape[1]), int(coords.y * frame.shape[0]))
            frame = cv2.circle(frame, center , 1, (0,0,255), 10)
            
            
            hs = MouseStatus.MOVE | MouseStatus.ABSOLUTE #lhand_status if result.handedness[i][0].category_name == 'Left' else rhand_status

            match gesture:
                case "Thumb_Up":
                    hs |= MouseStatus.WHEEL
                case "Thumb_Down":
                    hs |= MouseStatus.WHEEL 
                case "Closed_Fist":
                    hs |= MouseStatus.LMOUSE_DOWN 
                case _:
                    hs |= (MouseStatus.LMOUSE_UP if previous & MouseStatus.LMOUSE_DOWN else MouseStatus.IDLE)
            previous = hs
            client.send(MsgType.hand_update(coords.x, coords.y, hs)) #TODO: Priority hand?
        '''
        # display landmarks
        hand_result = hands.process(frame)
        if hand_result.multi_hand_landmarks:
            for landmarks in hand_result.multi_hand_landmarks:
                drawingModule.draw_landmarks(frame, landmarks, handsModule.HAND_CONNECTIONS)
            for i, handedness in enumerate(hand_result.multi_handedness): # enumerate every detected hand 
                hand = 0 if handedness.classification[0].label == "Left" else 1
                hand_data = [hand]
                
                for landmark in hand_result.multi_hand_landmarks[i].landmark: # Normalized landmarks
                    hand_data.append(landmark.x)
                    hand_data.append(landmark.y)
                    hand_data.append(landmark.z)
                for landmark in hand_result.multi_hand_world_landmarks[i].landmark: # World landmarks
                    hand_data.append(landmark.x)
                    hand_data.append(landmark.y)
                    hand_data.append(landmark.z)
                
                x = tensor(np.array([hand_data])).type(float32).to(device)
                gesture_id = str(argmax(gesture_model(x)).item())#str(gesture_model.predict([hand_data]).argmax())
                gesture = config['gestures'][gesture_id]

                hand_coords = hand_result.multi_hand_landmarks[i].landmark[0]

                center = (int(hand_coords.x * frame.shape[1]), int(hand_coords.y * frame.shape[0]))
                frame = cv2.circle(frame, center , 1, (0,0,255), 10)    
                
                hs = MouseStatus.MOVE | MouseStatus.ABSOLUTE | int(config['controls'][gesture_id])
                control = config['controls'][gesture_id]
                previous = hs

                cv2.putText(frame, gesture, (10*(i+1),50), cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,255),1,2)
        
        cv2.imshow("test", cv2.resize(frame, (0, 0), fx = 0.5, fy = 0.5))
        delta = DELAY - (delta - time.time() * 1000)
        if delta >= 1: cv2.waitKey(int(delta))
        if cv2.pollKey() & 0xFF == ord('q'): 
            break
        timestamp += DELAY
    camera.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-recognizer', '-r', type=Path, default='Models/default', dest='model_path')
    parser.add_argument('-vidx', '-v', type=int, default=0, dest='video_index')
    parser.add_argument('--gpu', action=BooleanOptionalAction, default=True, dest='gpu')
    args = parser.parse_args()
    device = torch.device('cuda' if torch.cuda.is_available() and args.gpu else 'cpu')
    print(device)
    startRecognizer(args.model_path, args.video_index, device)