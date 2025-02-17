import json
from pathlib import Path
from cursor import MouseStatus

'''
config file data:
'gesture_count' : int - Number of gestures model recognizes
'gestures' : {'str (idx)' : 'str (name)'} - Model's output indexes linked to gesture's name
'controls' : {'str (idx)' : int} - Model's output indexes linked to MouseStatus flags
'''

ACTIONNAMES = ['Left click', 'Right click', 'Middle click', 'Scroll up', 'Scroll down']

ActionName = {
    MouseStatus.LMOUSE_DOWN : "Left click",
    MouseStatus.RMOUSE_DOWN : "Right click",
    MouseStatus.MIDDLE_DOWN : "Middle click",
    MouseStatus.WHEEL : "Scroll up"
}

class ConfigKey():
    GESTURECOUNT = "gesture_count"
    GESTURES = "gestures"
    CONTROLS = "controls"

model_config = None

def load_config_file(model_path : Path, set : bool = True):
    global model_config
    try:
        with open(f"{model_path}/config.json") as f:
            mc = json.load(f)
            if set: model_config = mc
            return mc
    except IOError as e:
        print(e)
        print("Model path needs to link to directory.")
    return None

def valid_config_file(config_file : dict):
    if config_file is None: return False
    if not ConfigKey.GESTURECOUNT in config_file or not ConfigKey.GESTURES in config_file or not ConfigKey.CONTROLS in config_file:
        return False
    
    gc = config_file[ConfigKey.GESTURECOUNT]
    gestures = config_file[ConfigKey.GESTURES]
    controls = config_file[ConfigKey.CONTROLS]
    if (len(gestures) != gc or len(controls) != gc):
        return False
    
    for i in range(gc):
        si = str(i)
        if not si in gestures or not si in controls: 
            return False 
        if type(gestures[si]) != str or type(controls[si]) != int:
            return False

    return True