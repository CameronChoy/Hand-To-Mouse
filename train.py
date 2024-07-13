import os
import tensorflow as tf
# old numpy = 2.0.0
# old ml-dtypes = 0.4.0
assert tf.__version__.startswith('2')

from mediapipe_model_maker import gesture_recognizer

import matplotlib.pyplot as plt

def main():
    dataset_path = r'D:\VisionProject\gesture_data'
    data = gesture_recognizer.Dataset.from_folder(
    dirname=dataset_path,
    hparams=gesture_recognizer.HandDataPreprocessingParams()
    )

    train_data, rest_data = data.split(0.8)
    validation_data, test_data = rest_data.split(0.5)

    hparams = gesture_recognizer.HParams(export_dir="exported_model")
    options = gesture_recognizer.GestureRecognizerOptions(hparams=hparams)
    model = gesture_recognizer.GestureRecognizer.create(
        train_data=train_data,
        validation_data=validation_data,
        options=options
    )
    loss, acc = model.evaluate(test_data, batch_size=1)
    print(f"Test loss:{loss}, Test accuracy:{acc}")
    model.export_model()

if __name__ == '__main__':
    main()