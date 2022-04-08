from . import state_space
import networkx as nx


class Graph:
    # class to define graph
    # aggregates networkx.graph

    def __init__(self, graph, start="S", goal="G"):
        # graph is a networkx.Graph object
        #  add heurstic value as node attribute "h"
        #  add cost as edge attribute "cost"
        # start is the start node (default "S")
        # goal is the goal node (default "G")
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

    def plot(self, positions):
        # plots graph
        # positions is a dictionary {node: [x, y]} where [x, y] is the node coordinate
        heuristic = nx.get_node_attributes(self.graph, "h")
        if heuristic:  # h toevoegen aan de node labels
            labels = {node: str(node) + "\n" + str(h) for node, h in heuristic.items()}
        else:
            labels = {node: str(node) for node in self.graph.nodes}
        nx.draw(self.graph, positions, labels=labels, node_size=750, node_color="y")
        cost = nx.get_edge_attributes(self.graph, 'cost')
        if cost:
            nx.draw_networkx_edge_labels(self.graph, positions, cost)

    def search(self, Method, rules=None, print_result=True, print_queue=False):
        # searches path from start to goal node
        # Method is search.Algorithm class
        # rules is list of ProductionRule objects
        #  by default nodes are selected in alphabetic order
        # print_result is boolean, default is True
        # print_queue is boolean, default is False
        initial_state = State(self, self.start, rules)
        initial_path = Path([initial_state])
        method = Method(PathSeries([initial_path]), print_result=print_result, print_queue=print_queue)
        method.search()
        return method.path_to_goal

    @staticmethod
    def create(edges, start="S", goal="G"):
        # creates Graph object from given nodes and edges
        # edges is list of [node1, node2] pairs
        # start is the start node (default "S")
        # goal is the goal node (default "G")
        graph = nx.Graph()
        for node in {node for edge in edges for node in edge}:
            graph.add_node(node)
        for edge in edges:
            graph.add_edge(edge[0], edge[1])
        return Graph(graph, start, goal)


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

    @staticmethod
    def create_all(graph, reverse=False, key=None):
        # creates all possible production rules for a given graph
        # graph is a Graph object
        # returns a list of ProductionRule objects
        # by default the vertices are sorted in ascending order (reverse=False)
        # if reverse is True, the vertices are sorted in descending order
        # it is also possible to pass a function to order the vertices
        # assign this function to parameter key, which is None by default
        # check built-in function "sorted" for more information about parameters "reverse" and "key"
        vertices = sorted(graph.vertices, reverse=reverse, key=key)
        return [ProductionRule(vertex) for vertex in vertices]


class Move(state_space.Move):
    # class to define a graph move
    # inherits from state_space.Move

    def __init__(self, state, rule):
        # state is a State object
        # rule is a ProductionRule object
        edge = state.graph.edges[(state.vertex, rule.next_vertex)]  # cost is a graph edge attribute
        super().__init__(state, rule, edge["cost"] if "cost" in edge else 1)

    def __repr__(self):
        # overrides inherited __repr__ method
        # returns string with the name of the next vertex
        return str(self.rule)


class State(state_space.State):
    # class to define graph state
    # inherits from state_space.State

    def __init__(self, graph, vertex, rules=None):
        # graph is a networx.Graph object
        # vertex is the current node in graph (string)
        # rules is a list of ProductionRule objects
        #  by default nodes are selected in alphabetic order
        super().__init__(rules=ProductionRule.create_all(graph) if rules is None else rules)
        self.graph = graph
        self.vertex = vertex

    def is_valid_move(self, move):
        # checks if move is valid
        # move is Move object
        # returns boolean
        return any([self.vertex in edge and move.rule.next_vertex in edge for edge in self.graph.edges])

    def apply_move(self, move):
        # applies move to state self to get new state
        # move is Move object
        # returns new State object
        return State(self.graph, move.rule.next_vertex, self.rules)

    def is_goal(self):
        # checks if state self is a goal state
        # returns boolean
        return self.vertex == self.graph.goal

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

    def __init__(self, states):
        # states is a list of State objects
        super().__init__(states)

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

    def __repr__(self):
        # overrides inherited __repr__ method
        # returns string
        paths = ",".join([str(path) for path in self])
        return f"[{paths}]"
