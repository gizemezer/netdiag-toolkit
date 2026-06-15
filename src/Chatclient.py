import select
import socket
import sys
import signal
import pickle
import struct
import threading


CHAT_SERVER_NAME = 'server'


def send(channel, *args):
    #Sends data over socket
    buffer = pickle.dumps(args)#convert byteseries
    value = socket.htonl(len(buffer))
    size = struct.pack("L", value)
    channel.send(size) #Send size first
    channel.send(buffer) #Then send actual data

def receive(channel):
    #Receives data over socket and deserializes it

    size_data = channel.recv(struct.calcsize("L"))
    try:
        # Convert from network byte order to host byte order
        size = socket.ntohl(struct.unpack("L", size_data)[0])
    except struct.error as e:
        return ''
    # Empty byte buffer to hold data
    buf = b""

    while len(buf) < size:#/ Loop until all data is received
        buf += channel.recv(size - len(buf))
    return pickle.loads(buf)[0]

class ChatClient:
    def __init__(self, name, port, host):
        self.name = name
        self.connected = False
        self.host = host
        self.port = port
        # Initial prompt
        self.prompt = '[' + '@'.join((name, socket.gethostname().split('.')[0])) + ']> '
        # Connect to server at port
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((host, self.port))
            print("Now connected to chat server @ port {}".format(self.port))
            self.connected = True
            # Send my name...
            send(self.sock, 'NAME: ' + self.name)
            data = receive(self.sock)
            # Contains client address, set it
            addr = data.split('CLIENT: ')[1]
            self.prompt = '[' + '@'.join((self.name, addr)) + ']> '
        except socket.error as e:
            print("Failed to connect to chat server @ port {}".format(self.port))
            sys.exit(1)

    def run(self):
        #Chat client main loop
        def input_thread():
            # This thread handles user input from the console.


            while self.connected:#While connection is active read line from user
                line = sys.stdin.readline().strip()
                if line:
                    send(self.sock, line)

        # Start the input thread
        t = threading.Thread(target=input_thread, daemon=True)
        t.start()

        try:
            # Main thread: receive messages from the server.
            while self.connected:
                data = receive(self.sock)
                if not data:
                    print("Client shutting down.")
                    self.connected = False
                    break
                else:
                    # Print received messages
                    print("\n" + data)
                    # Optionally, reprint the prompt:
                    sys.stdout.write(self.prompt)
                    sys.stdout.flush()
        except KeyboardInterrupt:
            print("Client interrupted.")
        finally:
            self.sock.close()

