"""
This is the main entry point into the program
Need to call Bellman-Ford and subscriber here
"""
import selectors
import socket
import sys
from datetime import datetime

import fxp_bytes_subscriber


class Lab3(object):

    def __init__(self, address):
        self.selector = selectors.DefaultSelector()
        self.listener, self.address = self.start_a_server()
        self.graph = {}
        self.last_quoted = {}
        self.max_time = datetime(1970, 1, 1)

    def run(self):
        self.selector.register(self.listener, selectors.EVENT_WRITE)
        next_timeout = 0.2
        byte_stream = fxp_bytes_subscriber.serialize_address(self.address[0],
                                                             self.address[1])
        self.listener.sendto(byte_stream, ('127.0.0.1', 63000))

        while True:
            events = self.selector.select(next_timeout)
            for key, mask in events:
                # TODO: Remove stale quotes
                self.remove_stale_quotes()
                data = self.listener.recv(4096)
                self.iterate_through_data(data)

    @staticmethod
    def start_a_server():
        listener = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        listener.bind(('localhost', 0))
        return listener, listener.getsockname()

    def iterate_through_data(self, data):
        iterations = len(data) / 32
        for i in range(int(iterations)):
            message = fxp_bytes_subscriber.unmarshal_message(data[i*32:(i+1)*32])
            print(self.print(message))
            if message[0] >= self.max_time:
                self.max_time = message[0]
                self.add_to_graph(message)
            else:
                print('ignoring out-of-sequence message')

    def add_to_graph(self, message):
        timestamp = message[0]
        c1 = message[1]
        c2 = message[2]
        weight = message[3]
        combined = c1 + c2

        self.last_quoted[combined] = timestamp

        if c1 not in self.graph.keys():
            self.graph[c1] = {c2: weight}
        else:
            self.graph[c1][c2] = weight
        if c2 not in self.graph.keys():
            self.graph[c2] = {c1: 1/weight}
        else:
            self.graph[c2][c1] = 1/weight

    def print(self, message):
        message_string = ''
        message_string += str(message[0]) + ' '
        message_string += message[1] + ' '
        message_string += message[2] + ' '
        message_string += str(message[3])
        return message_string

    def remove_stale_quotes(self):
        if self.last_quoted:
            for key, value in list(self.last_quoted.items()):
                if(datetime.utcnow() - value).total_seconds() > 1.5:
                    curr1 = key[0:3]
                    curr2 = key[3:6]
                    del self.last_quoted[key]
                    try:
                        del self.graph[curr1][curr2]
                        del self.graph[curr2][curr1]
                    except KeyError as e:
                        continue
                    print(
                        'removing stale quote for (' + curr1 + ', ' + curr2 + ')')


if __name__ == '__main__':
    lab3 = Lab3(sys.argv[1:3])
    lab3.run()
