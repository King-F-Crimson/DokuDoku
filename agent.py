import random

from game import Game

class Agent:
    def __init__(self, game):
        self.game = game
        self.action_index = 0

    def get_action(self):
        if self.game.selected_shape == None:
            return random.randrange(100, 103)
        else:
            return random.randrange(0, 100)


if __name__ == "__main__":
    game = Game()
    agent = Agent(game)

    game.run(agent)