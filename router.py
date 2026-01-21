import random

class Router:
    def __init__(self, name):
        self.name = name
        self.connections = []
        self.maximum_recieving = random.randint(4, 10)
        self.recieving_now = 0

    def accept_connection(self, node):
        if self.recieving_now >= self.maximum_recieving:
            return False

        self.connections.append(node.name)
        self.recieving_now += 1
        return True

    def can_accept(self):
        return self.recieving_now < self.maximum_recieving
