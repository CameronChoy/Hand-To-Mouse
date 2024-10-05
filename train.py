import os
import tensorflow as tf
import numpy as np
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

    data = []
    label = []
    id = 0
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
        id += 1
    
    data = np.asarray(data)
    label = np.asarray(label)
    
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
        batch_size=64,
        epochs=100,
        validation_data=(x_test, y_test),
    )

    results = model.evaluate(x_test, y_test, batch_size=128)
    print("test loss, test acc:", results)

    os.chdir('..')
    model.save('model', save_format='tf')
    print(model.summary())
    #m = load_model('model')
    #results = m.evaluate(x_test, y_test, batch_size=128)
    #print("test loss, test acc:", results)
    return

if __name__ == '__main__':
    main()
