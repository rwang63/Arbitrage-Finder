"""
CPSC 5520, Seattle University
This is free and unencumbered software released into the public domain.
:Author: Ruifeng Wang
:Version: Fall2020
"""
from datetime import datetime
from math import log


class BellmanFord(object):
    """
    The BellmanFord object stores a graph constructed with quotes of conversions
    from one currency to another. There is a function to run the Bellman-Ford
    algorithm, which finds the shortest paths from a starting vertex to every
    other vertex and additionally will detect if there is a negative cycle.
    Additionally, it is checked if the negative edge is included in a cycle
    that leads back to the original currency.
    """
    def __init__(self):
        """
        Constructs a BellmanFord object that contains all the properties to
        store a graph and run the Bellman-Ford algorithm
        :param self:
        :return:
        """
        self.graph = {}  # Stores the graph
        self.last_quoted = {}  # Keeps tracks of when the quote was added

    def add_to_graph(self, message):
        """
        Deciphers and adds a quote to the graph
        :param message: Quote to be added to graph (list format)
        :return: None
        """
        timestamp = message[0]
        c1 = message[1]
        c2 = message[2]
        weight = message[3]
        combined = (c1, c2)

        self.last_quoted[combined] = timestamp

        # Storing the weight without converting using log base 10
        # The conversion is done in the Bellman-Ford algorithm
        # Reasoning is to know which direction I'm heading on the currency graph
        # Positive is from c1 to c2, negative is from c2 to c1
        if c1 not in self.graph.keys():
            self.graph[c1] = {c2: weight}
        else:
            self.graph[c1][c2] = weight
        if c2 not in self.graph.keys():
            self.graph[c2] = {c1: -weight}
        else:
            self.graph[c2][c1] = -weight

    def remove_stale_quotes(self):
        """
        Removes stale quotes (older than 1.5 seconds) from the graph
        :return: None
        """
        if self.last_quoted:
            for key, value in list(self.last_quoted.items()):
                if (datetime.utcnow() - value).total_seconds() > 1.5:
                    curr1 = key[0]
                    curr2 = key[1]

                    del self.last_quoted[key]
                    # Was getting key error when trying to remove from the graph
                    # but this try-except solved it
                    try:
                        del self.graph[curr1][curr2]
                        del self.graph[curr2][curr1]
                    except KeyError:
                        continue
                    print('removing stale quote for (\'' + curr1 + '\', \''
                          + curr2 + '\')')

    def get_vertices(self):
        """
        Returns all vertices of the graph
        :return: All vertices of the graph
        """
        return self.graph.keys()

    def get_exchange_rate(self, curr1, curr2):
        """
        Gets the exchange rate (edge) between curr1 to curr2
        :param curr1: First currency
        :param curr2: Second currency
        :return: Exchange rate (edge) between the two currencies
        """
        return self.graph[curr1][curr2]

    def shortest_paths(self, start_vertex, tolerance=0.0001):
        """
        Find the shortest paths (sum of edge weights) from start_vertex to every
        other vertex. Also detect if there are negative cycles and report one of
        them. Edges may be negative.

        For relaxation and cycle detection, we use tolerance. Only relaxations
        resulting in an improvement greater than tolerance are considered. For
        negative cycle detection, if the sum of weights is greater than
        -tolerance it is not reported as a negative cycle. This is useful when
        circuits are expected to be close to zero.

        >>> g = BellmanFord({'a': {'b': 1, 'c':5}, 'b': {'c': 2, 'a': 10}, 'c': {'a': 14, 'd': -3}, 'd': {}, 'e': {'a': 100}})
        >>> dist, prev, neg_edge = g.shortest_paths('a')
        >>> [(v, dist[v]) for v in sorted(dist)]  # shortest distance from 'a' to each other vertex
        [('a', 0), ('b', 1), ('c', 3), ('d', 0), ('e', inf)]
        >>> [(v, prev[v]) for v in sorted(prev)]  # last edge in shortest paths
        [('a', None), ('b', 'a'), ('c', 'b'), ('d', 'c'), ('e', None)]
        >>> neg_edge is None
        True
        >>> bf = BellmanFord({'a': {'b': 1, 'c': 5, 'e': -200}, 'b': {'c': 2, 'a': 10}, 'c': {'a': 14, 'd': -3}, 'd': {}, 'e': {'a': 100}})
        >>> dist, prev, neg_edge = bf.shortest_paths('a')
        >>> neg_edge  # edge where we noticed a negative cycle
        ('e', 'a')

        :param start_vertex: start of all paths
        :param tolerance: only if a path is more than tolerance better will
                          it be relaxed
        :return: distance, predecessor, negative_cycle
            distance:       dictionary keyed by vertex of shortest distance from
                            start_vertex to that vertex
            predecessor:    dictionary keyed by vertex of previous vertex in
                            shortest path from start_vertex
            negative_cycle: None if no negative cycle, otherwise an edge, (u,v),
                            in one such cycle
            cycle: The vertices in the negative cycle, in reverse order
        """

        negative_edge = None
        dist = {}
        prev = {}

        # Start by initializing the dist to all vertices as infinity
        for vertex in self.graph.keys():
            dist[vertex] = float("Inf")
        dist[start_vertex] = 0  # Distance from start to itself is 0
        prev[start_vertex] = None  # Predecessor of start vertex is None

        # This relaxes the edges, finding the shortest distance from the
        # start vertex to every other vertex (stored in dist)
        for _ in range(len(self.graph.keys()) - 1):
            for c1, edges in self.graph.items():
                for c2, weight in edges.items():
                    # If the weight is greater than 0, then we are going from c1
                    # to c2, so we use -log base 10, otherwise we are going from
                    # c2 to c1 and use log base 10 (must take absolute value of
                    # the weight since we stored the -)
                    if weight > 0:
                        weight = -log(weight, 10)
                    else:
                        weight = log(abs(weight), 10)
                    if dist[c1] != float("Inf") and dist[c1] + \
                            weight < dist[c2]:
                        if dist[c2] - (dist[c1] + weight) >= tolerance:
                            dist[c2] = dist[c1] + weight
                            prev[c2] = c1

        for key in dist:
            if dist[key] == float("Inf"):
                prev[key] = None

        found = False
        potential_cycle = []

        # Additional step to find if a negative edge exists
        for c1, edges in self.graph.items():
            for c2, weight in edges.items():
                potential_cycle.clear()
                # If the weight is greater than 0, then we are going from c1
                # to c2, so we use -log base 10, otherwise we are going from
                # c2 to c1 and use log base 10 (must take absolute value of
                # the weight since we stored the -)
                if weight > 0:
                    weight = -log(weight, 10)
                else:
                    weight = log(abs(weight), 10)
                if dist[c1] != float("Inf") and dist[c1] + \
                        weight < dist[c2]:

                    negative_edge = (c2, c1)

                    ending_vertex = negative_edge[0]

                    potential_cycle = [ending_vertex]
                    curr_vertex = prev[ending_vertex]

                    # This loop checks if the negative edge is a part of
                    # a cycle according to the prev
                    # If it is, the found variable is flipped to True
                    while True:
                        if ending_vertex == curr_vertex:
                            potential_cycle.append(curr_vertex)
                            found = True
                            break
                        elif curr_vertex in potential_cycle:
                            found = False
                            break
                        else:
                            potential_cycle.append(curr_vertex)
                            curr_vertex = prev[curr_vertex]
            # Found the cycle
            if found:
                break
        # Did not find the cycle, so we will mark negative_edge as None and
        # and empty the cycle
        if not found:
            negative_edge = None
            potential_cycle.clear()

        return dist, prev, negative_edge, potential_cycle
