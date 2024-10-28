import os
import numpy as np
import json
import time
from pathlib import Path
from argparse import ArgumentParser, BooleanOptionalAction
# old numpy = 2.0.0
# old ml-dtypes = 0.4.0
#from mediapipe_model_maker import gesture_recognizer

from torch.utils.data import DataLoader, random_split
from torch.optim import Adam
import torch
from torch import int64, float32, no_grad, save, argmax
from torch.nn import Linear, ReLU, Dropout, Softmax, Module, CrossEntropyLoss
from torchinfo import summary
from sklearn.model_selection import train_test_split
import model
from model import gr_torch_model
    
'''
Trains and saves model to a given directory name in Models

config data saved as json file in directory:
- 'gesture_count' tells range of values model outputs
- 'gestures' link model's output to gesture name
- 'controls' link model's output to MouseStatus flag indicating action
config_data = {
    'gesture_count' : int
    'gestures' : {
        Model output val (str) : Gesture Name (str),
    }

    'controls' : {
        Model output val (str) : MouseStatus flag (int)
    }

}
'''
def train_model(name : Path, epoches : int = 100, batch_size : int = 64, device : torch.device = torch.device('cpu')):
    model_path, ext = os.path.splitext(name)
    model_path, name = os.path.split(model_path)
    using_cuda = device == torch.device('cuda')
    try:
        os.chdir(r'gesture_data')
    except OSError as e:
        print(e)
        return

    data = []
    label = []
    id = 0
    config_data = {'gestures' : {}, 'controls' : {}}
    for dir in os.listdir():
        data_path = f"{dir}\data"
        if not os.path.isdir(data_path): 
            print(f"Could not find \'{data_path}\'")
            continue
        print(f"Retrieving \'{data_path}\' data")
        count = 0
        for f in os.listdir(data_path):
            d = np.load(f"{data_path}\{f}")
            count += len(d['arr_0'])
            for h in d['arr_0']: 
                data.append(h[1:]) # first value in data is imagenum, don't need
                label.append(id)
            print(f"found {count} images")
        config_data['gestures'][int(id)] = dir
        config_data['controls'][int(id)] = 1<<id
        id += 1
    config_data['gesture_count'] = id
    
    # shuffle and split dataset
    x_train, x_test, y_train, y_test = train_test_split(data, label)
    train_set = DataLoader(list(zip(x_train, y_train)),batch_size=batch_size, pin_memory=True if using_cuda else False)
    test_set = DataLoader(list(zip(x_test, y_test)),batch_size=batch_size, pin_memory=True if using_cuda else False)   
    
    model = gr_torch_model(id).to(device)
    loss = CrossEntropyLoss()
    opt = Adam(model.parameters())
    model.train()
    
    # Training
    running_tloss = 0
    for epoch in range(epoches):
        running_tloss = 0
        correct = 0
        for i, (x,label) in enumerate(train_set):
            x = x.type(float32).to(device)
            label = label.type(int64).to(device)
            opt.zero_grad()
            y = model(x)
            l = loss(y, label)
            l.backward()
            opt.step()
            running_tloss += l.item()
            _, p = torch.max(y,1)
            correct += (label == p).float().sum()
        accuracy = correct / len(y_train)
        running_tloss /= i+1
        print(f"Training epoch {epoch+1} loss: {running_tloss} acc: {accuracy}")
    train_acc = accuracy

    # Evaluation
    model.eval()
    running_vloss = 0
    correct = 0
    with no_grad():
        for i, (x, label) in enumerate(test_set):
            x = x.type(float32).to(device)
            label = label.type(int64).to(device)
            y = model(x)
            l = loss(y, label)
            running_vloss += l.item()
            _, p = torch.max(y,1)
            correct += (label == p).float().sum()
    accuracy = correct / len(y_test)
    print(f"Training loss: {running_tloss}\tValidation loss: {running_vloss/i+1}")
    print(f"Training acc: {train_acc}\tValidation acc: {accuracy}")
    
    # Saving
    os.chdir('..')
    try:
        model_path = f"Models/{name}"
        os.makedirs(model_path,exist_ok=True)
        os.chdir(model_path)
    except OSError as e:
        print(e)
        return
    save(model, 'model.pt')
    with open(f"config.json","w") as f:
        json.dump(config_data,f)
    '''
    x = np.array([x_train[0]])
    d = torch.tensor(x).type(float32)
    d = d.to(device)
    print(argmax(model(d)).item(), y_train[0])
    '''

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-name', '-n', type=Path, default=f"Model-{time.strftime('%Y-%m-%d--%H-%M-%S')}", dest='name')
    parser.add_argument('-epoches', '-e', type=int, default=100, dest='epoches')
    parser.add_argument('-batch', '-b', type=int, default=64, dest='batch_size')
    parser.add_argument('--use_gpu', '--g', action=BooleanOptionalAction, default=True, dest='gpu')
    args = parser.parse_args()
    train_model(args.name, args.epoches, args.batch_size, torch.device('cuda' if torch.cuda.is_available() and args.gpu else 'cpu'))
