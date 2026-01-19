class Client:
    name = ''
    connections = []

    def __init__(self, name, connections):
        self.name = name
        self.connections = connections