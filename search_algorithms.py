from abc import ABC, abstractmethod
from copy import deepcopy
from time import time
import numpy as np
from random import randint


class SearchAlgorithm(ABC):
    # abstract superclass for implementing search algorithms

    name = ""  # name of algorithm (string)

    def __init__(self, initial_queue, print_result=True, print_queue=False, depth_limit=np.Inf):
        # initial_queue is PathSeries object
        # print_result is boolean, default is True
        # print_queue is boolean, default is False
        # depth_limit limits search to given depth, default is Inf, meaning there is no limit
        self.initial_queue = initial_queue
        self.print_result = print_result
        self.print_queue = print_queue
        self.depth_limit = depth_limit
        self._initialize()

    def _initialize(self):
        # initializes attributes
        # called by constructor and by method search
        self.path_to_goal = None
        self.goal_is_reached = False
        self._queue = deepcopy(self.initial_queue)
        self._queue_class = type(self.initial_queue)
        self.length_queue = [len(self._queue)]
        self.elapsed_time = None
        self.nr_iterations = 0
        self._first_path = None
        self._new_paths = None

    def search(self):
        # performs the implemented search algorithm

        # start time
        starttime = time()

        # initialize
        self._initialize()

        # print initial queue
        self._print_initial_queue()

        # 2. while (queue is not empty and goal is not reached)
        self.goal_is_reached = self._queue[0].reaches_goal()
        if self.goal_is_reached:
            self.path_to_goal = self._queue[0]
        while self._queue and not self.goal_is_reached:

            # augment number of iterations
            self.nr_iterations += 1

            # length queue
            self.length_queue.append(len(self._queue))

            # remove the first path from the queue
            self._first_path = self._queue.pop(0)

            # check depth_limit
            if len(self._first_path) < self.depth_limit:

                # create new paths (to all children)
                # reject the new paths with loops
                self._new_paths = self._queue_class([path for path in self._first_path.calculate_children()
                                                     if not path.has_loop()])

                # add the new paths to the queue
                self._add_new_paths_to_queue()

                # print queue
                self._print_queue()

                # update goal_is_reached
                for path in self._new_paths:
                    if path.reaches_goal():
                        self.goal_is_reached = True
                        self.path_to_goal = path
                        break

        # elapsed time
        self.elapsed_time = time() - starttime

        # print path to goal
        self._print_path_to_goal()

        # print result
        self._print_result()

    def _print_result(self):
        # prints result
        # if self.print_result is True
        if self.print_result:
            # 3. if (goal reached) then success else failure
            print("ALGORITHM:", self.name)
            print("RESULT:", "SUCCES" if self.goal_is_reached else "FAILURE")
            # print elapsed time, number of iterations, and maximum length of queue
            print("Elapsed time:", self.elapsed_time, 'seconds')
            print('Number of iterations:', self.nr_iterations)
            print('Maximum length of queue:', max(self.length_queue))

    def _print_initial_queue(self):
        # prints initial queue
        # if self.print_queue is True
        if self.print_queue:
            print("Initial queue:")
            print(self._queue)
            print()

    def _print_queue(self):
        # prints queue
        # if self.print_queue is True
        if self.print_queue:
            print(f"Iteration {self.nr_iterations}")
            print("Path removed from queue:")
            print(self._first_path)
            print("New paths:")
            print(self._new_paths)
            print("Paths in queue:")
            print(self._queue)
            print()

    def _print_path_to_goal(self):
        # prints path to goal
        # if self.print_result is True and path to goal if found
        if self.print_queue and self.path_to_goal is not None:
            print("Path to goal found in new paths:")
            print(self.path_to_goal)
            print()

    @abstractmethod
    def _add_new_paths_to_queue(self):
        # adds new child paths to queue
        pass


class DFS(SearchAlgorithm):
    # class that implements depth-first search

    name = "Depth-first search"

    def __init__(self, initial_queue, print_result=True, print_queue=False, depth_limit=np.Inf):
        super().__init__(initial_queue, print_result, print_queue, depth_limit)

    def _add_new_paths_to_queue(self):
        # adds the new paths to the FRONT of the queue
        self._queue = self._queue_class(self._new_paths) + self._queue


class BFS(SearchAlgorithm):
    # class that implements breadth-first search

    name = "Breadth-first search"

    def __init__(self, initial_queue, print_result=True, print_queue=False):
        super().__init__(initial_queue, print_result, print_queue)

    def _add_new_paths_to_queue(self):
        # adds the new paths to the BACK of the queue
        self._queue = self._queue + self._queue_class(self._new_paths)


class NDS(SearchAlgorithm):
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


class IDS(SearchAlgorithm):
    # class that implements iterative deepening search

    name = "Iterative deepening search"

    def __init__(self, initial_queue, print_result=True, print_queue=False):
        super().__init__(initial_queue, print_result, print_queue)
        # create DFS object for depth-limited search
        self.__depth_limited_dfs = DFS(initial_queue, print_result, print_queue)

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
            self.path_to_goal = self._queue[0]

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
            self.length_queue += self.__depth_limited_dfs.length_queue

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

    def _add_new_paths_to_queue(self):
        pass
