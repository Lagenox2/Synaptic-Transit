class Network:
    def __init__(self):
        self.clients = []
        self.routers = []
        self.servers = []

    def add_client(self, client):
        self.clients.append(client)

    def add_router(self, router):
        self.routers.append(router)

    def add_server(self, server):
        self.servers.append(server)