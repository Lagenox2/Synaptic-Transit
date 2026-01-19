import random


class Router:
    maximum_recieving = 0
    recieving_now = 0

    def __init__(self):
        self.maximum_recieving = random.random() * (10 - 4) + 4