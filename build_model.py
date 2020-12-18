import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

def build_model(input_size, output_size):
    model = keras.Sequential()
    model.add(layers.Dense(input_size, input_dim=input_size, activation='relu'))
    model.add(layers.Dense(64, activation="relu", name="dense_1"))
    model.add(layers.Dense(64, activation="relu", name="dense_2"))
    model.add(layers.Dense(output_size, activation="relu", name="dense_3"))
    model.compile(optimizer="Adam", loss="mse", metrics=["mae"])
    print(model.summary())

    return model