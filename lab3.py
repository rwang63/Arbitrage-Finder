"""
CPSC 5520, Seattle University
This is free and unencumbered software released into the public domain.
:Author: Ruifeng Wang
:Version: Fall2020
"""

import socket
from datetime import datetime

import fxp_bytes_subscriber
import bellman_ford


def display_quote(message):
    """
    Takes in a quote as a list and parses it into a string
    :param message: list form of quote
    :return: quote as a string
    """
    message_string = ''
    message_string += str(message[0]) + ' '
    message_string += message[1] + ' '
    message_string += message[2] + ' '
    message_string += str(message[3])
    return message_string


class Lab3(object):
    """
    This program allows us to connect with a publisher as a subscriber and
    continuously receive UDP datagrams. These datagrams contain currency
    conversion quotes. Using these quotes, we store them in a graph and run
    Bellman-Ford at each update to check if there is an arbitrage opportunity.
    (Converting currencies and ending up at the original currency with more
    money than you started with.) If an arbitrage opportunity presents itself,
    we report it, otherwise we continue to receive messages from the publisher.
    """
    def __init__(self):
        """
        Constructs a lab 3 object
        """
        self.listener, self.address = self.start()
        self.most_recent = datetime(1970, 1, 1)
        self.sub_time = datetime.utcnow()
        self.g = bellman_ford.BellmanFord()

    def run(self):
        """
        Loops to run program while connected to publisher
        :return: None
        """

        # Serialize address before sending to publisher
        byte_stream = fxp_bytes_subscriber.serialize_address(self.address[0],
                                                             self.address[1])
        self.listener.sendto(byte_stream, ('127.0.0.1', 50403))

        while True:
            self.g.remove_stale_quotes()
            data = self.listener.recv(4096)
            self.iterate_through_data(data)
            self.run_bellman()

    @staticmethod
    def start():
        """
        Creates a connection with the server
        :return: socket and socket address tuple
        """
        listener = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        listener.bind(('localhost', 0))
        return listener, listener.getsockname()

    def iterate_through_data(self, data):
        """
        Iterates through the received quote, unmarshalling, printing and
        adding the quote to the graph as appropriate
        Ignores quotes that are sent out of sequence
        :param data: Quote directly from publisher
        :return: None
        """
        # Can be more than 1 quote per message, and each quote is 32 bytes
        # So need to find out how many iterations you need to decode
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
        """
        Runs the Bellman-Ford algorithm from each vertex until a negative
        cycle is found or all vertices have been cycled through
        :return: None
        """
        vertices = self.g.get_vertices()

        # Runs Bellman-Ford starting from every vertex in the graph looking for
        # an arbitrage opportunity
        # If one is found and a cycle is returned, we print it and stop
        for key in vertices:
            dist, prev, neg_edge, cycle = self.g.shortest_paths(key)

            if len(cycle) > 0:
                cycle.reverse()
                self.print_arbitrage(cycle)
                break

    def print_arbitrage(self, arbitrage_path):
        """
        Takes in the arbitrage path and prints the result.
        Does the calculation of conversions along the way
        :param arbitrage_path: List of vertices in the arbitrage opportunity
        """
        value = 100
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
    """
    Main entry point into the program
    Creates a Lab3 object and runs
    """
    lab3 = Lab3()
    lab3.run()
