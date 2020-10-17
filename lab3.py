"""
This is the main entry point into the program
Need to call Bellman-Ford and subscriber here
"""
import socket
from datetime import datetime

import fxp_bytes_subscriber
import bellman_ford


def display_quote(message):
    message_string = ''
    message_string += str(message[0]) + ' '
    message_string += message[1] + ' '
    message_string += message[2] + ' '
    message_string += str(message[3])
    return message_string


class Lab3(object):

    def __init__(self):
        self.listener, self.address = self.start_a_server()
        self.most_recent = datetime(1970, 1, 1)
        self.g = bellman_ford.BellmanFord()

    def run(self):
        byte_stream = fxp_bytes_subscriber.serialize_address(self.address[0],
                                                             self.address[1])
        self.listener.sendto(byte_stream, ('127.0.0.1', 63000))

        # while True:
        for _ in range(2):
            # curr1, curr2, stale =
            self.g.remove_stale_quotes()
            # if stale:
            #     print(
            #         'removing stale quote for (' + curr1 + ', ' + curr2 + ')')
            data = self.listener.recv(4096)
            self.iterate_through_data(data)
            self.detect_arbitrage()

    @staticmethod
    def start_a_server():
        listener = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        listener.bind(('localhost', 0))
        return listener, listener.getsockname()

    def iterate_through_data(self, data):
        iterations = len(data) / 32
        for i in range(int(iterations)):
            message = fxp_bytes_subscriber.unmarshal_message(
                data[i * 32:(i + 1) * 32])
            print(display_quote(message))
            if message[0] >= self.most_recent:
                self.most_recent = message[0]
                self.g.add_to_graph(message)
            else:
                print('ignoring out-of-sequence message')

    def detect_arbitrage(self):
        dist = {}
        prev = {}
        neg_edge = None
        arbitrage = []
        previous_vert = None
        vertices = self.g.get_vertices()
        for key in vertices:
            dist, prev, neg_edge = self.g.shortest_paths(key)
            # TODO break if you find a negative edge here?
        print(neg_edge)
        print(prev)
        if neg_edge is not None:
            for _ in range(len(vertices)):
                previous_vert = prev[neg_edge[1]]
            while True:
                arbitrage.append(previous_vert)
                if len(arbitrage) > 1 and previous_vert == neg_edge[1]:
                    break
                previous_vert = prev[previous_vert]
            arbitrage.reverse()
            for x in arbitrage:
                print(x, end=' ')
        else:
            print('No Arbitrage')
        print('\n')


if __name__ == '__main__':
    lab3 = Lab3()
    lab3.run()
