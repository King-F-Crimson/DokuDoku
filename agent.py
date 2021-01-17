from game import Game

import signal
import random

import numpy as np

from keras.models import Sequential
from keras.layers import Dense, Activation, Flatten
from keras.optimizers import Adam

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

physical_devices = tf.config.list_physical_devices('GPU') 
tf.config.experimental.set_memory_growth(physical_devices[0], True)

class Agent:
    def __init__(self, game):
        self.game = game

        self.exploration_rate = 0.25

        self.input_size = (game.board_size ** 2) + ((game.shape_size ** 2) * (game.shape_selection_count + 1))
        self.output_size = (game.board_size ** 2) + game.shape_selection_count

        # Try to load existing model.
        # Create new model if one does not exist.
        try:
            self.model = keras.models.load_model("model")
        except IOError:
            self.model = self.build_model(self.input_size, self.output_size)

        self.reward = 0

        self.state_history  = []
        self.action_history = []
        self.reward_history = []

    def build_model(self, input_size, output_size):
        model = keras.Sequential()
        model.add(layers.Dense(input_size, input_dim=input_size, activation='relu'))
        model.add(layers.Dense(200, activation="relu", name="dense_1"))
        model.add(layers.Dense(200, activation="relu", name="dense_2"))
        model.add(layers.Dense(output_size, activation="relu", name="dense_3"))
        model.compile(optimizer="Adam", loss="mse", metrics=["mae"])
        print(model.summary())

        return model

    def get_state(self):
        state = []

        # 0-99: board
        for row in self.game.board:
            for block in row:
                state.append(block)

        # 100-174: shapes, 25 for each shape
        for shape in self.game.shape_selection:
            for row in shape:
                for block in row:
                    state.append(block)
        # Fill empty shape slots with False
        state += [False] * (175 - len(state))

        # 175-199: selected shape if any
        if self.game.selected_shape != None:
            for row in self.game.selected_shape:
                for block in row:
                    state.append(block)
        else:
            # If none is selected fill with False
            state += [False] * 25

        return np.array(state).reshape(-1, self.input_size)

    def get_valid_options(self):
        actions = [False] * 103
        if self.game.selected_shape == None:
            for i in range(len(self.game.shape_selection)):
                if self.game.is_shape_placeable(self.game.shape_selection[i]):
                    actions[100 + i] = True
        else:
            for x in range(10):
                for y in range(10):
                    if self.game.is_placeable(self.game.selected_shape, x, y):
                        actions[x + (y * 10)] = True

        return actions

    def get_action(self):
        state = self.get_state()

        # Do random valid actions
        if np.random.rand() <= self.exploration_rate:
            try:
                action = self.get_valid_options().index(True)
            except ValueError:
                action = 0
        else:
            action = np.argmax(self.model.predict(state))
        
        self.state_history.append(state)
        self.action_history.append(action)

        return action

    def set_reward(self, reward):
        self.reward += reward

        self.reward_history.append(reward)

    def on_restart(self):
        self.reward = 0

        for i in range(len(self.action_history)):
            state = self.state_history[i]

            target_f = self.model.predict(state)
            target_f[0][self.action_history[i]] = self.reward_history[i]
            self.model.fit(state, target_f)

        self.reward_history = []
        self.action_history = []
        self.state_history = []

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.default_int_handler), 

    log = open("log.txt", 'a')
    game = Game()
    agent = Agent(game)

    try:
        game.run(agent, log)
    except KeyboardInterrupt:
        agent.model.save("model")

    log.close()
