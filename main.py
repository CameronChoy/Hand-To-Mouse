from gui import startGUI
from recognizer import start_recognizer
from config import load_config_file, valid_config_file
from threading import *
from time import sleep
from argparse import ArgumentParser, BooleanOptionalAction
from pathlib import Path
import torch
from model import gr_torch_model
import thread_data

recognizerThread = None

def startRecognizerThread():
    pass

def main():
    global recognizerThread
    parser = ArgumentParser()
    parser.add_argument('-recognizer', '-r', type=Path, default='Models/default', dest='model_path')
    parser.add_argument('-vidx', '-v', type=int, default=0, dest='video_index')
    parser.add_argument('--gpu', action=BooleanOptionalAction, default=True, dest='gpu')

    try:
        config = load_config_file(args.model_path)
        if not valid_config_file(config):
            print(f"Invalid config file at {args.model_path}")
    except IOError as e:
        print(e)

    args = parser.parse_args()
    device = torch.device('cuda' if torch.cuda.is_available() and args.gpu else 'cpu')

    recognizerThread=Thread(target=start_recognizer, args=(args.model_path, args.video_index, device)) 
    recognizerThread.start() 
    startGUI()
    thread_data.exit_event.set()
    recognizerThread.join()
    print("exiting")
    

if __name__ == '__main__':
    main()