from .base import Base, Algorithm
from time import time
import numpy as np
from random import randint


class DFS(Algorithm):
    # class that implements depth-first search

    name = "Depth-first search"

    def __init__(self, initial_queue, print_result=True, print_queue=False, depth_limit=np.Inf):
        super().__init__(initial_queue, print_result, print_queue)
        self.depth_limit = depth_limit

    def _create_new_paths(self):
        # creates new children if length of first path is smaller than depth limit
        if len(self._first_path) < self.depth_limit:  # check depth_limit
            super()._create_new_paths()

    def _add_new_paths_to_queue(self):
        # adds the new paths to the FRONT of the queue
        if len(self._first_path) < self.depth_limit:  # check depth_limit
            self._queue = self._queue_class(self._new_paths) + self._queue

    def _check_goal_is_reached(self):
        if len(self._first_path) < self.depth_limit:  # check depth_limit
            super()._check_goal_is_reached()

    def _print_queue(self):
        if len(self._first_path) < self.depth_limit:  # check depth_limit
            super()._print_queue()


class BFS(Algorithm):
    # class that implements breadth-first search

    name = "Breadth-first search"

    def __init__(self, initial_queue, print_result=True, print_queue=False):
        super().__init__(initial_queue, print_result, print_queue)

    def _add_new_paths_to_queue(self):
        # adds the new paths to the BACK of the queue
        self._queue = self._queue + self._queue_class(self._new_paths)


class NDS(Algorithm):
    # class that implements non-deterministic search

    name = "Non-deterministic search"

    def __init__(self, initial_queue, print_result=True, print_queue=False):
        super().__init__(initial_queue, print_result, print_queue)

    def _add_new_paths_to_queue(self):
        # adds the new paths in RANDOM places in the queue
        for path in self._new_paths:
            # add child in RANDOM place in queue
            index = randint(0, len(self._queue))  # get random index
            self._queue.insert(index, path)


class IDS(Base):
    # class that implements iterative deepening search

    name = "Iterative deepening search"

    def __init__(self, initial_queue, print_result=True, print_queue=False):
        super().__init__(initial_queue, print_result, print_queue)
        # create DFS object for depth-limited search
        self.__depth_limited_dfs = DFS(initial_queue, print_result, print_queue)
        self.depth_limit = None

    def search(self):

        # start time
        starttime = time()

        # initialize
        self._initialize()

        # 1. DEPTH = 1
        self.depth_limit = 1

        # 2. WHILE goal is not reached
        self.goal_is_reached = self.initial_queue[0].reaches_goal()
        if self.goal_is_reached:
            self.path_to_goal = self.initial_queue[0]

        while not self.goal_is_reached:

            # print depth limit
            if self.print_result or self.print_queue:
                print('--> DEPTH:', self.depth_limit)

            # perform Depth-limited search
            self.__depth_limited_dfs.depth_limit = self.depth_limit
            self.__depth_limited_dfs.search()
            if self.print_result or self.print_queue:
                print()

            # check if goal is reached
            self.path_to_goal = self.__depth_limited_dfs.path_to_goal
            self.goal_is_reached = self.path_to_goal is not None

            # number of iterations
            self.nr_iterations += self.__depth_limited_dfs.nr_iterations

            # length queue
            self.queue_lengths += self.__depth_limited_dfs.queue_lengths

            # DEPTH = DEPTH + 1
            self.depth_limit += 1

        # elapsed time
        self.elapsed_time = time() - starttime

        # print result
        self._print_result()

    def _print_result(self):
        if self.print_result:
            print("--> FINAL RESULT")
            super()._print_result()
