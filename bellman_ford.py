from datetime import datetime
from math import log


class BellmanFord(object):

    def __init__(self):
        self.graph = {}
        self.last_quoted = {}
        # self.dist = {}
        # self.prev = {}

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
            self.graph[c2] = {c1: -weight}
        else:
            self.graph[c2][c1] = -weight

    def remove_stale_quotes(self):
        if self.last_quoted:
            for key, value in list(self.last_quoted.items()):
                if (datetime.utcnow() - value).total_seconds() > 1.5:
                    curr1 = key[0:3]
                    curr2 = key[3:6]

                    del self.last_quoted[key]

                    try:
                        del self.graph[curr1][curr2]
                        del self.graph[curr2][curr1]
                    except KeyError:
                        continue
                    print('removing stale quote for (\'' + curr1 + '\', \''
                          + curr2 + '\')')

    def get_vertices(self):
        return self.graph.keys()

    def get_exchange_rate(self, curr1, curr2):
        return self.graph[curr1][curr2]

    def shortest_paths(self, start_vertex, tolerance=0):
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
        """
        # print('The graph is:')
        # print(self.graph)

        negative_edge = None
        dist = {}
        prev = {}

        for vertex in self.graph.keys():
            dist[vertex] = float("Inf")
        dist[start_vertex] = 0
        prev[start_vertex] = None

        # loop to relax edges
        for _ in range(len(self.graph.keys()) - 1):
            for c1, edges in self.graph.items():
                for c2, weight in edges.items():
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

        # loop to find negative edge
        for c1, edges in self.graph.items():
            for c2, weight in edges.items():
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

                    # print(negative_edge)
                    # print(prev)

                    while True:
                        if ending_vertex == curr_vertex:
                            potential_cycle.append(curr_vertex)
                            found = True
                            break
                        elif curr_vertex in potential_cycle:
                            potential_cycle = []
                            found = False
                            break
                        else:
                            potential_cycle.append(curr_vertex)
                            curr_vertex = prev[curr_vertex]
                    # for _ in range(len(dist)):
                    #     if ending_vertex != curr_vertex:
                    #         curr_vertex = prev[curr_vertex]
                    #     elif ending_vertex == curr_vertex:
                    #         found = True
                    #         break
            if found:
                # print('cycle', potential_cycle)
                break

        if not found:
            negative_edge = None
        # print(self.dist)
        # print(self.prev)
        # print(negative_edge)

        return dist, prev, negative_edge
