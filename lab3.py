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
        self.sub_time = datetime.utcnow()
        self.g = bellman_ford.BellmanFord()

    def run(self):
        byte_stream = fxp_bytes_subscriber.serialize_address(self.address[0],
                                                             self.address[1])
        self.listener.sendto(byte_stream, ('127.0.0.1', 63000))

        while True:
            self.g.remove_stale_quotes()
            data = self.listener.recv(4096)
            self.iterate_through_data(data)
            self.run_bellman()
            if self.check_sub_time():
                print('Subscription has ended')
                break

    @staticmethod
    def start_a_server():
        listener = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        listener.bind(('localhost', 0))
        return listener, listener.getsockname()

    def check_sub_time(self):
        if (datetime.utcnow() - self.sub_time).total_seconds() > 120:
            return True
        return False

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

    def run_bellman(self):
        # dist = {}
        # prev = {}
        # neg_edge = None

        vertices = self.g.get_vertices()

        for key in vertices:
            dist, prev, neg_edge = self.g.shortest_paths(key)

            # print(neg_edge)
            # print(prev)
            if neg_edge is not None:
                correct_path = self.get_arbitrage_cycle(dist, prev, neg_edge)
                if correct_path:
                    break

    def get_arbitrage_cycle(self, dist, prev, neg_edge):
        # arbitrage.append(neg_edge[1])
        # print('this is the negative edge', neg_edge)
        previous_vert = neg_edge[0]
        arbitrage_path = [previous_vert]
        curr_vertex = prev[previous_vert]
        while True:
            if previous_vert == curr_vertex:
                arbitrage_path.append(curr_vertex)
                break
            elif curr_vertex in arbitrage_path:
                break
            else:
                arbitrage_path.append(curr_vertex)
                curr_vertex = prev[curr_vertex]

        arbitrage_path.reverse()
        correct_path = self.print_arbitrage(arbitrage_path)
        return correct_path

    def print_arbitrage(self, arbitrage_path):
        # print('passed in path', arbitrage_path)
        value = 100
        if arbitrage_path is None:
            return False
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
        return True


if __name__ == '__main__':
    lab3 = Lab3()
    lab3.run()
