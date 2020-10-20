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
        # curr1, curr2, stale =
        self.g.remove_stale_quotes()
        # if stale:
        #     print(
        #         'removing stale quote for (' + curr1 + ', ' + curr2 + ')')
        data = self.listener.recv(4096)
        self.iterate_through_data(data)
        arbitrage_result = self.detect_arbitrage()
        self.print_arbitrage(arbitrage_result)

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
        vertices = self.g.get_vertices()

        # TODO: Fix this for loop
        # TODO: Need to do something with the shortest path each time it's run
        for key in vertices:
            dist, prev, neg_edge = self.g.shortest_paths(key)

        print(neg_edge)
        print(prev)
        if neg_edge is not None:
            # arbitrage.append(neg_edge[1])
            previous_vert = neg_edge[1]
            while True:
                if len(arbitrage) > len(dist):
                    break
                arbitrage.append(previous_vert)
                if len(arbitrage) > 1 and previous_vert == neg_edge[1]:
                    break
                previous_vert = prev[previous_vert]
            arbitrage.reverse()
            return arbitrage
        else:
            return None

    def print_arbitrage(self, arbitrage_path):
        print(arbitrage_path)
        value = 100
        if arbitrage_path is None:
            return
        else:
            print('ARBITRAGE:')
            print('\t start with', arbitrage_path[0], '100')
            for i in range(len(arbitrage_path) - 1):
                exchange_rate = self.g.get_exchange_rate(
                    arbitrage_path[i], arbitrage_path[i+1])

                if exchange_rate > 0:
                    exchange_rate = exchange_rate
                else:
                    exchange_rate = 1 / abs(exchange_rate)

                value *= exchange_rate
                print('\t', arbitrage_path[i], 'for', arbitrage_path[i + 1],
                      'at', exchange_rate, '-->', arbitrage_path[i + 1], value)


if __name__ == '__main__':
    lab3 = Lab3()
    lab3.run()
    # TODO: end after 1 minute
