import sys
import time
from client import Client, MsgType, MouseStatus
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

    camera.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_FRAME_WIDTH)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_FRAME_HEIGHT)
    camera.set(cv2.CAP_PROP_FPS, FPS)
    camera.set(cv2.CAP_PROP_FOURCC, FOURCC)

    BaseOptions = mp.tasks.BaseOptions
    GestureRecognizer = mp.tasks.vision.GestureRecognizer
    GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions
    VisionRunningMode = mp.tasks.vision.RunningMode
    drawingModule = mp.solutions.drawing_utils
    handsModule = mp.solutions.hands
    

    options = GestureRecognizerOptions(
        base_options=BaseOptions(model_asset_path="exported_model/gesture_recognizer.task"),
        running_mode=VisionRunningMode.VIDEO, num_hands=2)

    recognizer = GestureRecognizer.create_from_options(options)

    hands = handsModule.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)

    previous = MouseStatus.IDLE

    timestamp = 0
    while True:
        ret, frame = camera.read()
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
        result = recognizer.recognize_for_video(mp_image, timestamp)
        for idx, landmarks in enumerate(result.hand_landmarks):
            coords = landmarks[0]
            gesture = result.gestures[idx][0].category_name

            center = (int(coords.x * frame.shape[1]), int(coords.y * frame.shape[0]))
            frame = cv2.circle(frame, center , 1, (0,0,255), 10)
            cv2.putText(frame, gesture, (10,50), cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,255),1,2)
            
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

        # display landmarks
        hand_result = hands.process(frame)
        if hand_result.multi_hand_landmarks:
            for landmarks in hand_result.multi_hand_landmarks:
                drawingModule.draw_landmarks(frame, landmarks, handsModule.HAND_CONNECTIONS)
        cv2.imshow("test", cv2.resize(frame, (0, 0), fx = 0.5, fy = 0.5))
        if cv2.waitKey(DELAY) & 0xFF == ord('q'): 
            break
        timestamp += DELAY
    camera.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()