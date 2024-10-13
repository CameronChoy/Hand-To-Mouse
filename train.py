import os
import tensorflow as tf
import numpy as np
import json
import time
from pathlib import Path
from argparse import ArgumentParser
# old numpy = 2.0.0
# old ml-dtypes = 0.4.0
assert tf.__version__.startswith('2')

#from mediapipe_model_maker import gesture_recognizer

import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow import keras
from keras import layers
#from keras.models import load_model
from sklearn.model_selection import train_test_split

# 
# Input: 42x3 landmarks normalized and world, 1x1 handness
# Output: M x 1 one hot for M given gestures to learn
class gr_model(keras.Model):
    def __init__(self, gesture_count):
        super().__init__()
        self.M = gesture_count

        #self.input1 = layers.InputLayer(input_shape=(1,127))
        self.dense1 = layers.Dense(128, "relu")
        self.dense2 = layers.Dense(64, "relu")
        self.dense3 = layers.Dense(self.M, "softmax")
        

    
    def call(self, data):
        x = self.dense1(data)
        x = self.dense2(x)
        return self.dense3(x)
    


def main():
    dataset_path = r'gesture_data'
    try:
        os.chdir(dataset_path)
    except OSError as e:
        print(e)
        exit(1)
    
    parser = ArgumentParser()
    parser.add_argument('-name', '-n', type=Path, default=f"Model-{time.strftime('%Y-%m-%d--%H-%M-%S')}", dest='name')
    parser.add_argument('-epoches', '-e', type=int, default=100, dest='epoches')
    parser.add_argument('-batch', '-b', type=int, default=64, dest='batch')
    args = parser.parse_args()

    data = []
    label = []
    id = 0
    gestures = {}
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
        gestures[id] = dir
        id += 1
    
    data = np.asarray(data)
    label = np.asarray(label)
    print(gestures)
    
    # shuffle and split dataset
    x_train, x_test, y_train, y_test = train_test_split(data, label)
    
    print(f"Retrieved data {data.shape} {label.shape}")

    model = gr_model(id)
    model.compile(
        optimizer=keras.optimizers.Adam(),
        loss=keras.losses.SparseCategoricalCrossentropy(),
        metrics=[keras.metrics.SparseCategoricalAccuracy()],
    )   
    

    history = model.fit(
        x_train,
        y_train,
        batch_size=args.batch,
        epochs=args.epoches,
        validation_data=(x_test, y_test),
    )

    results = model.evaluate(x_test, y_test)
    print("test loss, test acc:", results)

    
    os.chdir('..')
    try:
        os.chdir("Models")
    except OSError as e:
        print(e,"\nCreating Models dir")
        os.mkdir("Models")
        os.chdir("Models")

    model.save(args.name, save_format='tf')
    print(model.summary())
    with open(f"{args.name}/gestures.json","w") as f:
        json.dump(gestures,f)
    #m = load_model('model')
    #results = m.evaluate(x_test, y_test, batch_size=128)
    #print("test loss, test acc:", results)
    return

if __name__ == '__main__':
    main()
