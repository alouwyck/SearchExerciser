# SearchExerciser is developed by Stefaan Haspeslagh and Andy Louwyck
# at Vives University of Applied Sciences, Kortrijk, Belgium.
# May 2022
from .base import Algorithm
import numpy as np
from itertools import permutations


class UC(Algorithm):
    # class that implements uniform cost

    name = "Uniform cost"

    def __init__(self, initial_queue, print_result=True, print_queue=False):
        super().__init__(initial_queue, print_result, print_queue)

    def _add_new_paths_to_queue(self):
        # adds the new paths to the front of the queue
        # sorts the entire queue by accumulated cost
        super()._add_new_paths_to_queue()
        self._queue = self._queue_class(sorted(self._queue, key=lambda path: path.cost))


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
        self._queue = self._queue_class(filter(lambda path: path.cost <= self._bound, self._queue))


class EEUC(OUC):
    # class that implements estimate extended uniform cost

    name = "Estimate extended uniform cost"

    def __init__(self, initial_queue, print_result=True, print_queue=False):
        super().__init__(initial_queue, print_result, print_queue)

    def _add_new_paths_to_queue(self):
        # adds the new paths to the front of the queue
        # sorts the entire queue by f-value (= accumulated cost + heuristic h)
        Algorithm._add_new_paths_to_queue(self)
        self._queue = self._queue_class(sorted(self._queue, key=lambda path: path.apply_heuristic() + path.cost))


class AS(EEUC):
    # class that implements A*

    name = "A*"

    def __init__(self, initial_queue, print_result=True, print_queue=False):
        super().__init__(initial_queue, print_result, print_queue)

    def _add_new_paths_to_queue(self):
        # adds the new paths to the front of the queue
        # sorts the entire queue by f-value (= accumulated cost + heuristic h)
        # deletes redundant paths
        super()._add_new_paths_to_queue()
        self._queue = self._queue_class([p for p, q in permutations(self._queue, 2)
                                         if not q.contains_state(p[-1]) or p.cost < q.cost])
