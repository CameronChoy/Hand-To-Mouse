import sys
import time
from client import Client, MsgType
import mediapipe as mp
import cv2

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

def main():
    if len(sys.argv) != 2:
        print("missing args, needs [port]")
        exit(1)
    try:
        port = int(sys.argv[1])
    except ValueError:
        print(f"Error: argument [port]='{sys.argv[1]}' must be an integer")
        exit(1)
    
    client = Client(('localhost',port))
    
    camera = cv2.VideoCapture(0)
    if camera is None or not camera.isOpened(): 
        print("No camera detected, ending process")
        return
    
    BaseOptions = mp.tasks.BaseOptions
    GestureRecognizer = mp.tasks.vision.GestureRecognizer
    GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions
    VisionRunningMode = mp.tasks.vision.RunningMode
    drawingModule = mp.solutions.drawing_utils
    handsModule = mp.solutions.hands
    

    options = GestureRecognizerOptions(
        base_options=BaseOptions(model_asset_path="D:/VisionProject/gesture_recognizer.task"),
        running_mode=VisionRunningMode.VIDEO, num_hands=2)

    recognizer = GestureRecognizer.create_from_options(options)

    hands = handsModule.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)

    lhand_status = HandStatus()
    rhand_status = HandStatus()

    timestamp = 0
    while True:
        ret, frame = camera.read()
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
        result = recognizer.recognize_for_video(mp_image, timestamp)
        for landmarks in result.hand_landmarks:
            coords = landmarks[9]
            center = (int(coords.x * frame.shape[1]), int(coords.y * frame.shape[0]))
            frame = cv2.circle(frame, center , 1, (0,0,255), 10)
            client.send(MsgType.hand_coords(coords.x, coords.y))
        
        for i, gesture in enumerate(result.gestures):
            g = gesture[0].category_name
            cv2.putText(frame, g, (10,50), cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,255),1,2)
            hs = lhand_status if result.handedness[i][0].category_name == 'Left' else rhand_status
            if g == 'Thumb_Up':
                if not hs.scroll_up:
                    client.send(MsgType.scroll_up_on())
                    hs.scroll_up = True
            else:
                if hs.scroll_up:
                    client.send(MsgType.scroll_up_off())
                    hs.scroll_up = False

            if g == 'Thumb_Down':
                if not hs.scroll_down:
                    client.send(MsgType.scroll_down_on())
                    hs.scroll_down = True
            else:
                if hs.scroll_down:
                    client.send(MsgType.scroll_down_off())
                    hs.scroll_down = False

            if g == 'Closed_Fist':
                if not hs.lmouse:
                    client.send(MsgType.lmouse_on())
                    hs.lmouse = True
            else:
                if hs.lmouse:
                    client.send(MsgType.lmouse_off())
                    hs.lmouse = False
            

        # display landmarks
        hand_result = hands.process(frame)
        if hand_result.multi_hand_landmarks:
            for landmarks in hand_result.multi_hand_landmarks:
                drawingModule.draw_landmarks(frame, landmarks, handsModule.HAND_CONNECTIONS)
        
        cv2.imshow("test", frame)
        if cv2.waitKey(16) & 0xFF == ord('q'): 
            break
        timestamp += 16
    camera.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()