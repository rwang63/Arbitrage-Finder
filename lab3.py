"""
This is the main entry point into the program
Need to call Bellman-Ford and subscriber here
"""
import selectors
import socket
import sys
import fxp_bytes_subscriber


class Lab3(object):

    def __init__(self, address):
        self.selector = selectors.DefaultSelector()
        self.listener, self.address = self.start_a_server()

    def run(self):
        self.selector.register(self.listener, selectors.EVENT_WRITE)
        next_timeout = 0.2
        data = None
        byte_stream = fxp_bytes_subscriber.serialize_address(self.address[0],
                                                             self.address[1])
        self.listener.sendto(byte_stream, ('127,0,0,1', 63000))

        while True:
            events = self.selector.select(next_timeout)
            for key, mask in events:
                data = self.listener.recv(4096)
            print(data)

    @staticmethod
    def start_a_server():
        listener = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        listener.bind(('localhost', 0))
        return listener, listener.getsockname()


if __name__ == '__main__':
    lab3 = Lab3(sys.argv[1:3])
    lab3.run()
