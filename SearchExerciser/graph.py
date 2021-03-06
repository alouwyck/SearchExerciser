# SearchExerciser is developed by Stefaan Haspeslagh and Andy Louwyck
# at Vives University of Applied Sciences, Kortrijk, Belgium.
# May 2022
from . import state_space
import numpy as np
import networkx as nx
import string
from itertools import combinations, product
import random


class Graph(state_space.Problem):
    # class to define graph
    # aggregates networkx.Graph object

    def __init__(self, graph, start="S", goal="G", rules=None):
        # graph is a networkx.Graph object
        #  add heuristic value as node attribute "h"
        #  add cost as edge attribute "cost"
        # start is the start node (default "S")
        # goal is the goal node (default "G")
        # rules is a list of nodes that indicates the order in which nodes are selected
        #  by default nodes are selected in alphabetic order
        super().__init__(ProductionRule.create_all(graph) if rules is None else rules)
        self.graph = graph
        self.start = start
        self.goal = goal

    @property
    def vertices(self):
        # returns self.graph.nodes
        return self.graph.nodes

    @property
    def edges(self):
        # returns self.graph.edges
        return self.graph.edges

    def _get_initial_queue(self):
        initial_state = State(self, self.start)
        initial_path = Path([initial_state])
        return PathSeries([initial_path])

    def distance_to_goal(self, vertex):
        # returns distance from given vertex to goal
        # which is the vertex' attribute "h"
        return self.graph.nodes[vertex]['h']

    def get_cost(self, edge):
        # returns the cost of given edge (tuple)
        # which is the edge's attribute "cost"
        if edge[1] in self.graph.neighbors(edge[0]) and 'cost' in self.graph[edge[0]][edge[1]]:
            return self.graph[edge[0]][edge[1]]['cost']
        else:
            return 1.0

    def plot(self, positions=None):
        # plots graph
        # positions is a dictionary {node: [x, y]} where [x, y] is the node coordinate
        #   if positions is not given, the networkx.spring_layout is used
        if positions is None:
            positions = nx.spring_layout(self.graph)
        heuristic = nx.get_node_attributes(self.graph, "h")
        if heuristic:  # add heuristic value h to node labels
            labels = {node: str(node) + "\n" + str(h) for node, h in heuristic.items()}
        else:
            labels = {node: str(node) for node in self.graph.nodes}
        nx.draw(self.graph, positions, labels=labels, node_size=750, node_color="y")
        cost = nx.get_edge_attributes(self.graph, 'cost')
        if cost:
            nx.draw_networkx_edge_labels(self.graph, positions, cost)

    @staticmethod
    def create(edges, start="S", goal="G", heuristic=None):
        # creates Graph object from given nodes and edges
        # edges is list of [node1, node2] pairs or [node1, node2, cost] if cost is relevant
        # start is the start node (default "S")
        # goal is the goal node (default "G")
        # heuristic is dict {node=h} with heuristic values, default is None
        graph = nx.Graph()
        for node in {node for edge in edges for node in edge[:2]}:
            graph.add_node(node)
        for edge in edges:
            if len(edge) == 2:
                graph.add_edge(edge[0], edge[1])
            else:
                graph.add_edge(edge[0], edge[1], cost=edge[-1])
        if heuristic is not None:
            for node, h in heuristic.items():
                graph.nodes[node]["h"] = h
        return Graph(graph, start, goal)

    @staticmethod
    def create_random(num_of_nodes=None, max_num_of_edges=3, min_cost=5, max_cost=10, seed=None):
        # creates random Graph object
        # the created graph consists of layers
        #   where the first layer consists of start node 'S'
        #   and the last layer contains the goal node 'G'
        # the total number of layers is len(num_of_nodes) + 2
        # where num_of_nodes is a list
        #   with num_of_nodes[i] the number of nodes in intermediate layer i
        #   default is [3, 4, 3]
        # max_num_of_edges is the maximum of number of edges between two layers
        # for each edge a random cost is generated between min_cost and max_cost
        #   default is between 5 and 10
        #   min_cost and max_cost must be positive integers
        # if seed is given, it is used to set seed for random module (int)
        if num_of_nodes is None:
            num_of_nodes = [3, 4, 3]
        if seed is not None:
            random.seed(seed)
        a = list(string.ascii_uppercase)
        a.remove('S')
        a.remove('G')
        n = sum(num_of_nodes)
        m = int(np.ceil(np.log(n) / np.log(len(a))))
        a = [''.join(letters) for letters in product(*([a] * m))]
        a = a[:n]
        a += ['G']
        h = max_cost * (len(num_of_nodes) + 1)
        num_of_nodes += [1]
        edges = []
        layer1 = {"S"}
        heuristic = dict(S=h)
        for i, n in enumerate(num_of_nodes):
            layer2 = set(a[:n])
            a = a[n:]
            h -= max_cost
            new_edges = [edge for edge in combinations(layer1.union(layer2), 2)]
            random.shuffle(new_edges)
            new_edges = new_edges[:max_num_of_edges]
            if i == 0 and 'S' not in {node for edge in new_edges for node in edge}:
                new_edges.append(('S', random.choice(new_edges)[0]))
            layer1 = {node for edge in new_edges for node in edge if node in layer2}
            heuristic.update({node: h for node in layer1})
            new_edges = [[node1, node2, random.randint(min_cost, max_cost)] for node1, node2 in new_edges]
            edges += new_edges
        return Graph.create(edges, heuristic=heuristic)


class ProductionRule(state_space.ProductionRule):
    # class to define a graph production rule
    # which comes down to selecting the next vertex
    # inherits from state_space.ProductionRule

    def __init__(self, next_vertex):
        # next_vertex is a node of the graph (string)
        super().__init__()
        self.next_vertex = next_vertex

    def __repr__(self):
        # overrides inherited __repr__ method
        # returns string with the name of the next vertex
        return str(self.next_vertex)

    def apply(self, state):
        # applies production rule self to given state
        # state is a State object
        # returns Move object
        edge = (state.vertex, self.next_vertex)
        return Move(state, self, state.graph.get_cost(edge))

    @staticmethod
    def create_all(graph, reverse=False, key=None):
        # creates all possible production rules for a given graph
        # graph is a networkx.Graph object
        # returns a list of ProductionRule objects
        # by default the vertices are sorted in ascending order (reverse=False)
        # if reverse is True, the vertices are sorted in descending order
        # it is also possible to pass a function to order the vertices
        # assign this function to parameter key, which is None by default
        # check built-in function "sorted" for more information about parameters "reverse" and "key"
        try:
            vertices = sorted(graph.nodes, reverse=reverse, key=key)
        except AttributeError:
            vertices = sorted(graph.vertices, reverse=reverse, key=key)
        return [ProductionRule(vertex) for vertex in vertices]


class Move(state_space.Move):
    # class to define a graph move
    # inherits from state_space.Move

    def __init__(self, state, rule, cost=0.0):
        # state is a State object
        # rule is a ProductionRule object
        super().__init__(state, rule, cost)

    def __repr__(self):
        # overrides inherited __repr__ method
        # returns string with the name of the next vertex
        return str(self.rule)


class State(state_space.State):
    # class to define graph state
    # inherits from state_space.State

    def __init__(self, graph, vertex):
        # graph is a Graph object
        # vertex is the current node in graph (string)
        super().__init__(graph)
        self.vertex = vertex

    @property
    def graph(self):
        return self.problem

    def is_valid_move(self, move):
        # checks if move is valid
        # move is Move object
        # returns boolean
        return move.rule.next_vertex in self.problem.graph.neighbors(self.vertex)

    def apply_move(self, move):
        # applies move to state self to get new state
        # move is Move object
        # returns new State object
        return State(self.graph, move.rule.next_vertex)

    def is_goal(self):
        # checks if state self is a goal state
        # returns boolean
        return self.vertex == self.graph.goal

    def apply_heuristic(self):
        # returns distance from current vertex to goal
        return self.graph.distance_to_goal(self.vertex)

    def __eq__(self, other):
        # overrides inherited __eq__ method
        # checks if state self is equal to other state
        # two states are the same if their current vertices are the same
        # returns boolean
        return self.vertex == other.vertex

    def __repr__(self):
        # overrides inherited __repr__ method
        # returns string with current vertex name
        return str(self.vertex)


class Path(state_space.Path):
    # class to define path in graph
    # inherits from state_space.Path

    def __init__(self, states, cost=0.0):
        # states is a list of State objects
        super().__init__(states, cost)

    def __repr__(self):
        # overrides inherited __repr__ method
        # returns string
        return "".join([str(state) for state in self])


class PathSeries(state_space.PathSeries):
    # class to define series of graph paths
    # inherits from state_space.PathSeries

    def __init__(self, paths):
        # paths is a list of Path objects
        super().__init__(paths)

    def string_to_print(self, attr=None, ndigits=1):
        # overrides inherited string_to_print method
        # returns string to print when printing queue of search algorithm
        # attr is None, 'h', 'c', of 'f'
        #  'h': add heuristic to string
        #  'c': add cost to string
        #  'f': add f-value to string
        # ndigits is the number of decimal places
        paths = ",".join([path.string_to_print(attr, ndigits) for path in self])
        return f"[{paths}]"

    def __repr__(self):
        # overrides inherited __repr__ method
        # returns string
        paths = ",".join([str(path) for path in self])
        return f"[{paths}]"
