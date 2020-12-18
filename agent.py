from game import Game

class Agent:
    def __init__(self, game):
        self.game = game
        self.action_index = 0

    def get_action(self):
        if self.action_index == 0:
            self.action_index += 1
            return 105
        else:
            return 0


if __name__ == "__main__":
    game = Game()
    agent = Agent(game)

    game.run(agent)