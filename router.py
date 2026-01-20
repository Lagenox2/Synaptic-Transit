import random

class Router:
    name = ''
    connections = []
    maximum_recieving = 0
    recieving_now = 0
    
    def __init__(self, name, connections):
        self.name = name
        self.connections = connections
        self.maximum_recieving = random.random() * (10 - 4) + 4
        self.recieving_now = 0