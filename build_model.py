import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

board_size = 10
shape_size = 5
shape_count = 3

input_size = (board_size ** 2) + ((shape_size ** 2) * shape_count)
output_size = (board_size ** 2) + shape_count

model = keras.Sequential()
model.add(keras.Input(shape=(input_size,)))
model.add(layers.Dense(64, activation="relu", name="dense_1"))
model.add(layers.Dense(64, activation="relu", name="dense_2"))
model.add(layers.Dense(output_size, activation="relu", name="dense_3"))

model.compile(loss='mse', optimizer=keras.optimizers.RMSprop())

model.summary()

# model.save("model")