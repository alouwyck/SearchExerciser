# SearchExerciser is developed by Stefaan Haspeslagh and Andy Louwyck
# at Vives University of Applied Sciences, Kortrijk, Belgium.
# May 2022
from .base import SearchAlgorithm
import numpy as np
from itertools import permutations


class UC(SearchAlgorithm):
    # class that implements uniform cost

    name = "Uniform cost"

    def __init__(self, initial_queue, print_result=True, print_queue=False):
        super().__init__(initial_queue, print_result, print_queue)
        self._print_options = dict(attr='c', ndigits=1)  # also print cost c

    def _add_new_paths_to_queue(self):
        # adds the new paths to the front of the queue
        # sorts the entire queue by accumulated cost
        super()._add_new_paths_to_queue()
        self._queue = self._queue_class(sorted(self._queue, key=lambda path: path.cost))

    def _print_result(self):
        # prints result
        # if self.print_result is True
        if self.print_result:
            super()._print_result()
            print('Accumulated cost of path to goal:', self.path_to_goal.cost)


class OUC(UC):
    # class that implements optimal uniform cost

    name = "Optimal uniform cost"

    def __init__(self, initial_queue, print_result=True, print_queue=False):
        super().__init__(initial_queue, print_result, print_queue)

    def _check_goal_is_reached(self):
        # updates goal_is_reached
        if self._queue[0].reaches_goal():  # only checks first path in queue!
            self.goal_is_reached = True
            self.path_to_goal = self._queue[0]


class BBUC(OUC):
    # class that implements branch-and-bound extended uniform cost

    name = "Branch-and-bound extended uniform cost"

    def __init__(self, initial_queue, print_result=True, print_queue=False):
        super().__init__(initial_queue, print_result, print_queue)
        self._bound = np.Inf
        self._pruned = None

    def _initialize(self):
        # initialize attributes
        # called by method search
        super()._initialize()
        self._bound = np.Inf

    def _add_new_paths_to_queue(self):
        # adds the new paths to the front of the queue
        # sorts the entire queue by accumulated cost
        # updates the upper bound
        # removes paths from the queue with cost greater than the upper bound
        super()._add_new_paths_to_queue()
        for path in self._new_paths:
            if path.reaches_goal():
                self._bound = min(path.cost, self._bound)
        if self.print_queue:
            self._pruned = self._queue_class(filter(lambda path: path.cost > self._bound, self._queue))
        self._queue = self._queue_class(filter(lambda path: path.cost <= self._bound, self._queue))

    def _print_queue(self):
        # prints queue
        # if self.print_queue is True
        if self.print_queue:
            print(f"Iteration {self.nr_iterations}")
            print("Path removed from queue:")
            print(self._first_path.string_to_print(**self._print_options))
            print("New paths:")
            print(self._new_paths.string_to_print(**self._print_options))
            if self._pruned:
                print("Pruned paths:")
                print(self._pruned.string_to_print(**self._print_options))
            print("Paths in queue:")
            print(self._queue.string_to_print(**self._print_options))
            print()


class EEUC(OUC):
    # class that implements estimate extended uniform cost

    name = "Estimate extended uniform cost"

    def __init__(self, initial_queue, print_result=True, print_queue=False):
        super().__init__(initial_queue, print_result, print_queue)
        self._print_options = dict(attr='f', ndigits=1)  # also print f-value

    def _add_new_paths_to_queue(self):
        # adds the new paths to the front of the queue
        # sorts the entire queue by f-value (= accumulated cost + heuristic h)
        SearchAlgorithm._add_new_paths_to_queue(self)
        self._queue = self._queue_class(sorted(self._queue, key=lambda path: path.apply_heuristic() + path.cost))


class AS(EEUC):
    # class that implements A*

    name = "A*"

    def __init__(self, initial_queue, print_result=True, print_queue=False):
        super().__init__(initial_queue, print_result, print_queue)
        self._redundant = None

    def _add_new_paths_to_queue(self):
        # adds the new paths to the front of the queue
        # sorts the entire queue by f-value (= accumulated cost + heuristic h)
        # deletes redundant paths
        super()._add_new_paths_to_queue()
        self._redundant = self._queue_class([p for p, q in permutations(self._queue, 2)
                                             if q.contains_state(p[-1]) and p.cost >= q.cost])
        self._queue = self._queue_class([path for path in self._queue if path not in self._redundant])

    def _print_queue(self):
        # prints queue
        # if self.print_queue is True
        if self.print_queue:
            print(f"Iteration {self.nr_iterations}")
            print("Path removed from queue:")
            print(self._first_path.string_to_print(**self._print_options))
            print("New paths:")
            print(self._new_paths.string_to_print(**self._print_options))
            if self._redundant:
                print("Redundant paths:")
                print(self._redundant.string_to_print(**self._print_options))
            print("Paths in queue:")
            print(self._queue.string_to_print(**self._print_options))
            print()
