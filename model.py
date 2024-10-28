import torch
from torch.nn import Linear, ReLU, Dropout, Softmax, Module
from torchinfo import summary
# 
# Input: 42x3 landmarks normalized and world, 1x1 handness
# Output: M x 1 probabilities one hot for M given gestures to learn

'''
import tensorflow as tf
from tensorflow import keras
assert tf.__version__.startswith('2')
from keras import layers
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
'''
class gr_torch_model(Module):
    def __init__(self, gesture_count, dropout_p = 0.5):
        super(gr_torch_model, self).__init__()
        self.dense1 = Linear(127,128)
        self.dense2 = Linear(128,64)
        self.dense3 = Linear(64, gesture_count)
        self.relu = ReLU()
        self.softmax = Softmax(dim=1)
        self.dropout = Dropout(dropout_p)
        self.float()
        
    
    def forward(self, x):
        x = self.dense1(x)
        x = self.relu(x)
        #x = self.dropout(x)
        x = self.dense2(x)
        x = self.relu(x)
        x = self.dense3(x)
        return self.softmax(x)