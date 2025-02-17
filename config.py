import json
from pathlib import Path

'''
config file data:
'gesture_count' : int - Number of gestures model recognizes
'gestures' : {'str (idx)' : 'str (name)'} - Model's output indexes linked to gesture's name
'controls' : {'str (idx)' : int} - Model's output indexes linked to MouseStatus flags
'''

ACTIONNAMES = ['Left click', 'Right click', 'Middle click', 'Scroll up', 'Scroll down']

class ConfigKeys():
    CONFIG_GESTURECOUNT = "gesture_count"
    CONFIG_GESTURES = "gestures"
    CONFIG_CONTROLS = "controls"

model_config = None


def load_config_file(model_path : Path):
    global model_config
    try:
        with open(f"{model_path}/config.json") as f:
            model_config = json.load(f)
            return model_config
    except IOError as e:
        print(e)
        print("Model path needs to link to directory.")
    return None

def valid_config_file(config_file : dict):
    if not ConfigKeys.CONFIG_GESTURECOUNT in config_file or not ConfigKeys.CONFIG_GESTURES in config_file or not ConfigKeys.CONFIG_CONTROLS in config_file:
        return False
    
    gc = config_file[ConfigKeys.CONFIG_GESTURECOUNT]
    gestures = config_file[ConfigKeys.CONFIG_GESTURES]
    controls = config_file[ConfigKeys.CONFIG_CONTROLS]
    if (len(gestures) != gc or len(controls) != gc):
        return False
    
    for i in range(gc):
        si = str(i)
        if not si in gestures or not si in controls: 
            return False 
        if type(gestures[si]) != str or type(controls[si]) != int:
            return False

    return True
