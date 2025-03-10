import sys
import time
import datetime
from datetime import datetime, timedelta
import numpy as np
from pathlib import Path
import json
from argparse import ArgumentParser, BooleanOptionalAction
from client import Client, MsgType, MouseStatus
import mediapipe as mp
import cv2
import torch
from torch import load, argmax, tensor, float32
from cursor import mouse_event
from model import gr_torch_model
import thread_data
from PIL import Image, ImageTk
from config import load_config_file, valid_config_file, ConfigKey
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
DELAY = 1000/FPS

# Marks plane in user's space with rect (size defined by user's hands) that represents the whole screen
# hand coordinates will be projected onto plane to find position relative to rect to calculate mouse position
def configure_hand_space(lhand, rhand):
    pass

def start_recognizer(model_path : Path, video_index : int, device : torch.device):
    
    camera = cv2.VideoCapture(video_index)
    if camera is None or not camera.isOpened(): 
        print("No camera detected, closing recognizer.")
        return

    try:
        gesture_model = load(f"{model_path}/model.pt", weights_only=False).to(device)#load_model(model_path)
        gesture_model.eval()
        config = load_config_file(model_path)
        if config is None:
            print(f"Failed to load config file at {model_path}, closing recognizer.")
            return
        if not valid_config_file(config):
            print(f"Invalid config file at {model_path}, closing recognizer")
            return
    except IOError as e:
        print(e)
        print("Model path needs to link to directory.")
        print(f"Failed to load model {model_path}, closing recognizer.")
        return
        
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_FRAME_WIDTH)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_FRAME_HEIGHT)
    camera.set(cv2.CAP_PROP_FPS, FPS)
    camera.set(cv2.CAP_PROP_FOURCC, FOURCC)

    drawingModule = mp.solutions.drawing_utils
    handsModule = mp.solutions.hands
    hands = handsModule.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)

    previous = MouseStatus.IDLE

    while not thread_data.exit_event.is_set():
        startTime = datetime.now() # amount of time in miliseconds to delay next loop
        ret, frame = camera.read()

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
                gesture_id = str(argmax(gesture_model(x)).item())
                gesture = config[ConfigKey.GESTURES][gesture_id]

                hand_coords = hand_result.multi_hand_landmarks[i].landmark[0]

                center = (int(hand_coords.x * frame.shape[1]), int(hand_coords.y * frame.shape[0]))
                frame = cv2.circle(frame, center , 1, (0,0,255), 10)    
                
                flags = MouseStatus.MOVE | MouseStatus.ABSOLUTE | int(config[ConfigKey.CONTROLS][gesture_id])
                if config[ConfigKey.CONTROLS][gesture_id] & MouseStatus.LMOUSE_DOWN == 0:
                    flags |= MouseStatus.LMOUSE_UP if previous & MouseStatus.LMOUSE_DOWN else MouseStatus.IDLE
                previous = flags

                normalized_coordinates = hand_result.multi_hand_landmarks[i].landmark[0]
                mouse_event(flags, normalized_coordinates.x, normalized_coordinates.y, 0)

                cv2.putText(frame, gesture, (10,50*(i+1)), cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,255),1,2)

        resizedframe = cv2.resize(frame, (0, 0), fx = 0.5, fy = 0.5)
        frame = cv2.cvtColor(resizedframe, cv2.COLOR_BGR2RGBA)
        thread_data.cameraView = Image.fromarray(frame)
        #cv2.imshow("test", resizedframe)

        timeToDelay = DELAY - (datetime.now() - startTime).microseconds / 1000
        if timeToDelay >= 1: key = cv2.waitKey(int(timeToDelay))
        else: key = cv2.pollKey()

        if key & 0xFF == ord('q'): 
            break
    camera.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-recognizer', '-r', type=Path, default='Models/default', dest='model_path')
    parser.add_argument('-vidx', '-v', type=int, default=0, dest='video_index')
    parser.add_argument('--gpu', action=BooleanOptionalAction, default=True, dest='gpu')
    args = parser.parse_args()
    device = torch.device('cuda' if torch.cuda.is_available() and args.gpu else 'cpu')
    start_recognizer(args.model_path, args.video_index, device)