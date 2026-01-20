import random

class Router:
    def __init__(self, name, connections):
        self.name = name
        self.connections = connections
        self.maximum_recieving = random.random() * (10 - 4) + 4
        self.recieving_now = 0