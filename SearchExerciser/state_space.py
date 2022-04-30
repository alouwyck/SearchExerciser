from abc import ABC, abstractmethod
from collections import UserList


class Problem(ABC):

    def __init__(self, rules):
        # rules: list of ProductionRule objects
        self.rules = rules

    def search(self, Method, print_result=True, print_queue=False):
        # searches path from start to goal
        # Method is a search.base.Algorithm class: DFS, BFS, NDS, IDS, HC, GS, BS, UC, OUC, BBUC, EEUC, AS
        # print_result: boolean, default is True
        # print_queue: boolean, default is False
        method = Method(self._get_initial_queue(), print_result, print_queue)
        method.search()
        return method.path_to_goal

    @abstractmethod
    def _get_initial_queue(self):
        pass


class State(ABC):
    # abstract class to represent states of a search problem

    def __init__(self, problem):
        # problem is Problem object
        self.problem = problem
        self.rules = problem.rules

    def apply_production_rules(self):
        # applies production rules self.rules to state self
        # returns list of Move objects
        return [rule.apply(self) for rule in self.rules]

    @abstractmethod
    def is_valid_move(self, move):
        # checks if given move is valid
        # move is a Move object
        # returns boolean
        pass

    @abstractmethod
    def apply_move(self, move):
        # applies move to state self
        # move is a Move object
        # returns a State object representing the new state
        pass

    @abstractmethod
    def is_goal(self):
        # checks if state self is the goal state
        # returns boolean
        pass

    @abstractmethod
    def apply_heuristic(self):
        # apply heuristic to state self
        # returns float
        pass

    @abstractmethod
    def __eq__(self, other):
        # overrides inherited __eq__ method
        # compares state self to other state
        # required to check if a path contains cycles
        # returns boolean
        pass


class ProductionRule:
    # class that implements a production rule
    # a production rule is an action that can be applied on the states in general
    # a production is therefore independent of a state

    def apply(self, state):
        # applies production rule self to given state
        # state is a State object
        # returns Move object
        return Move(state, self)


class Move:
    # class that implements a move
    # a move is a production rule that is applied to a given state

    def __init__(self, state, rule, cost=0.0):
        # state is a State object
        # rule is a ProductionRule object
        # cost is the cost of the move, default is 0
        self.state = state
        self.rule = rule
        self.cost = cost

    def is_valid(self):
        # checks if move self is valid
        # returns boolean
        return self.state.is_valid_move(self)

    def apply(self):
        # applies move self to self.state
        # returns State object representing the new state
        return self.state.apply_move(self)


class Path(UserList):
    # class to implement a path
    # a path is a series of states

    def __init__(self, states, cost=0.0):
        # states is a list of State objects
        # cost is the accumulated cost of the path (float)
        super().__init__(states)
        self.cost = cost

    def has_loop(self):
        # checks if path self contains cycles/loops
        # returns boolean
        return any([self[-1] == state for state in self[:-1]])  # checking last state is sufficient

    def contains_state(self, state):
        # checks if path self contains given state
        return state in self

    def reaches_goal(self):
        # checks if path self reaches the goal state
        # returns boolean
        return self[-1].is_goal()  # call is_goal() method on last state

    def apply_heuristic(self):
        # applies heuristic to last state in path self
        return self[-1].apply_heuristic()

    def calculate_children(self):
        # generates children of last state in path self
        # returns list containing these child paths
        moves = self[-1].apply_production_rules()  # apply production rules on last state
        return [self.__apply_move(move) for move in moves if move.is_valid()]  # apply moves if they are valid

    def __apply_move(self, move):
        # applies given move and adds resulting new state to path self
        # returns new Path object
        new_path = self + type(self)([move.apply()])
        new_path.cost = self.cost + move.cost
        return new_path

    def __repr__(self):
        # overrides inherited __repr__ method
        # returns string
        states = ", ".join([str(state) for state in self])
        return f"[{states}]"


class PathSeries(UserList):
    # class to implement a series of paths
    # e.g. the queue in search algorithms

    def __init__(self, paths):
        # paths is list of Path objects
        super().__init__(paths)

    def __repr__(self):
        # overrides inherited __repr__ method
        # returns string
        return "\n".join([str(path) for path in self])
