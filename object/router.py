import random

class Router:
    def __init__(self, name):
        self.name = name
        self.connected_clients = []
        self.connected_servers = []
        self.connected_routers = []
        self.max_connected = random.randint(5, 10)
        self.recieving_now = 0

    def add_client(self, client):
        if self.can_accept():
            self.connected_clients.append(client)
            self.recieving_now += 1

    def remove_client(self, client):
        if client in self.connected_clients:
            self.connected_clients.remove(client)
            self.recieving_now -= 1

    def connect_server(self, server):
        if self.can_accept():
            self.connected_servers.append(server)
            self.recieving_now += 1

    def disconnect_server(self, server):
        if server in self.connected_servers:
            self.connected_servers.remove(server)
            self.recieving_now -= 1

    def can_accept(self):
        return self.recieving_now < self.max_connected