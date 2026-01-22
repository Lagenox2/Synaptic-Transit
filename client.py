class Client:
    def __init__(self, name):
        self.name = name
        self.connections = []

    def connect(self, router):
        if router.name not in self.connections:
            if router.accept_connection(self):
                self.connections.append(router.name)
                return True
        return False

    def disconnect(self, router):
        if router.name in self.connections:
            self.connections.remove(router.name)
            router.remove_connection(self)
