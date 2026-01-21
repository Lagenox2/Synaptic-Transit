class Server:
    def __init__(self, name):
        self.name = name
        self.connections = []

    def connect(self, router):
        if router.name not in self.connections:
            self.connections.append(router.name)
            router.accept_connection(self)
