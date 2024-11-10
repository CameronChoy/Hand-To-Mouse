from gui import startGUI
from recognizer import startRecognizer
from threading import *
from argparse import ArgumentParser, BooleanOptionalAction
from pathlib import Path
import torch
from model import gr_torch_model
import thread_data


def main():
    parser = ArgumentParser()
    parser.add_argument('-recognizer', '-r', type=Path, default='Models/default', dest='model_path')
    parser.add_argument('-vidx', '-v', type=int, default=0, dest='video_index')
    parser.add_argument('--gpu', action=BooleanOptionalAction, default=True, dest='gpu')
    args = parser.parse_args()
    device = torch.device('cuda' if torch.cuda.is_available() and args.gpu else 'cpu')

    t1=Thread(target=startRecognizer, args=(args.model_path, args.video_index, device)) 
    t1.start() 
    startGUI()
    t1.join()
    

if __name__ == '__main__':
    main()