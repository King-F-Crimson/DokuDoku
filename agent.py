import random

from game import Game

class Agent:
    def __init__(self, game):
        self.game = game
        self.action_index = 0

    def get_state(self):
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
        q_table = self.get_state()
        try:
            return q_table.index(1)
        except ValueError:
            return 0

if __name__ == "__main__":
    game = Game()
    agent = Agent(game)

    game.run(agent)