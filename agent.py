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

        self.state_history = []
        self.prediction_history = []
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

    def get_valid_actions(self):
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

        valid_actions = self.get_valid_actions()

        prediction = self.model.predict(state)

        for i, action in enumerate(valid_actions):
            if not action:
                prediction[0][i] = -10

        action = np.argmax(prediction)

        # Do random valid actions if action is invalid or exploring
        # if np.random.rand() <= self.exploration_rate or not valid_actions[action]:
        #     try:
        #         action = valid_actions.index(True)
        #     except ValueError:
        #         action = 0
        
        self.state_history.append(state)
        self.prediction_history.append(prediction)
        self.action_history.append(action)

        return action

    def set_reward(self, reward):
        self.reward += reward

        self.reward_history.append(reward)

    def on_restart(self):
        self.reward = 0

        for i in range(len(self.action_history)):
            state = self.state_history[i]
            prediction = self.prediction_history[i]

            discount_factor = 0.8
            discounted_future_reward = 0
            for j, reward in enumerate(self.reward_history[i:]):
                discounted_future_reward += reward * pow(discount_factor, i)
            
            prediction[0][self.action_history[i]] = self.reward_history[i] + discounted_future_reward
            self.model.fit(state, prediction)

        self.reward_history = []
        self.action_history = []
        self.state_history = []
        self.prediction_history = []

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.default_int_handler), 

    log = open("log.txt", 'a')
    game = Game()
    agent = Agent(game)

    game.run(agent, log)

    agent.model.save("model")
    print("Saving model")

    log.close()
