import random

from game import Game
from build_model import build_model

from keras.models import Sequential
from keras.layers import Dense, Activation, Flatten
from keras.optimizers import Adam

import numpy as np

import tensorflow as tf
physical_devices = tf.config.list_physical_devices('GPU') 
tf.config.experimental.set_memory_growth(physical_devices[0], True)

class Agent:
    def __init__(self, game):
        self.game = game

        self.input_size = (game.board_size ** 2) + ((game.shape_size ** 2) * (game.shape_selection_count + 1))
        self.output_size = (game.board_size ** 2) + game.shape_selection_count

        self.model = build_model(self.input_size, self.output_size)

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

    def get_q_table(self):
        q_table = [0] * 103
        if self.game.selected_shape == None:
            for i in range(len(self.game.shape_selection)):
                if self.game.is_shape_placeable(self.game.shape_selection[i]):
                    q_table[100 + i] = 1
        else:
            for x in range(10):
                for y in range(10):
                    if self.game.is_placeable(self.game.selected_shape, x, y):
                        q_table[x + (y * 10)] = 1

        return q_table

    def get_action(self):
        action = np.argmax(self.model.predict(self.get_state()))
        print(action)
        return action

        q_table = self.get_q_table()
        try:
            return q_table.index(1)
        except ValueError:
            return 0

if __name__ == "__main__":
    game = Game()
    agent = Agent(game)

    game.run(agent)