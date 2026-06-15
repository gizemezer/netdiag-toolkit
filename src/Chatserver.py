import select
import socket
import sys
import signal
import pickle
import struct
import threading
import time


CHAT_SERVER_NAME = 'server'


def send(channel, *args):
    buffer = pickle.dumps(args)
    value = socket.htonl(len(buffer))
    size = struct.pack("L", value)

    channel.send(size)
    channel.send(buffer)

def receive(channel):
    size_data = channel.recv(struct.calcsize("L"))

    try:
        size = socket.ntohl(struct.unpack("L", size_data)[0])
    except struct.error as e:
        return ''
    buf = b""
    while len(buf) < size:
        buf += channel.recv(size - len(buf))
    return pickle.loads(buf)[0]

class ChatServer:

    def __init__(self, port,host, backlog=5):
        #Initializes chat server
        self.clients = 0#Number of connected clients
        self.clientmap = {}#Client soket  (adres, isim) mapping
        self.outputs = []#List of output sockets
        self.chat_log = []# Chat history
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)# re-using socket address
        self.server.bind((host, port))
        print("Server listening to port: {} ...".format(port))
        self.server.listen(backlog)


    def sighandler(self, signum, frame):
        #Clean up client outputs.
        print("Shutting down server...")
        self.save_chat_log()


        # Close existing client sockets
        for output in self.outputs:
            output.close()
        self.server.close()

        sys.exit(0)

    def get_client_name(self, client):
        #for returns client's name
        info = self.clientmap[client]
        host, name = info[0][0], info[1]
        return '@'.join((name, host))

    def save_chat_log(self):
        #Saves chat history to file
        if self.chat_log:
            filename = f"chat_log_server_{int(time.time())}.txt"#Filename: with timestamp


            with open(filename, 'w', encoding='utf-8') as f:
                f.write("=== CHAT LOG (SERVER) ===\n")
                for msg in self.chat_log:
                    f.write(msg + "\n")
            print(f"\nChat log saved to {filename}")


    def run(self):
        inputs = [self.server]
        self.outputs = []

        running = True

        while running:
            try:
                readable, writeable, exceptional = select.select(inputs, self.outputs, [])# select():Wait for ready sockets

            except select.error as e:
                break

            for sock in readable:
                if sock == self.server:#If it's the server socket

                    client, address = self.server.accept()
                    print("Chat server: got connection {} from {}".format(client.fileno(), address))
                    # Read the login name
                    cname = receive(client).split('NAME: ')[1]
                    # Compute client name and send back
                    self.clients += 1
                    send(client, 'CLIENT: ' + str(address[0]))
                    inputs.append(client)
                    self.clientmap[client] = (address, cname)
                    # Send  info to other clients
                    msg = "\n(Connected: New client ({}) from {})".format(self.clients, self.get_client_name(client))
                    for output in self.outputs:
                        send(output, msg)
                    self.outputs.append(client)
                else:
                    # handle client sockets: incoming messages
                    try:
                        data = receive(sock)
                        if data:
                            # Broadcast the message to all other clients
                            msg = "\n#[{}]>>{}".format(self.get_client_name(sock), data)
                            self.chat_log.append(msg)#log this message
                            print(msg)
                            for output in self.outputs:
                                if output != sock:
                                    send(output, msg)
                        else:
                            # Client disconnected
                            print("Chat server: {} hung up".format(sock.fileno()))
                            self.clients -= 1
                            sock.close()
                            inputs.remove(sock)
                            if sock in self.outputs:
                                self.outputs.remove(sock)
                            # Inform others of client departure
                            msg = "\n(Now hung up: Client from {})".format(self.get_client_name(sock))
                            for output in self.outputs:
                                send(output, msg)
                    except socket.error as e:
                        # Remove socket on error
                        if sock in inputs:
                            inputs.remove(sock)
                        if sock in self.outputs:
                            self.outputs.remove(sock)
                        sock.close()
                        print("Socket error: {}".format(e))


