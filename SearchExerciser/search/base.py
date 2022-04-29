from abc import ABC, abstractmethod
from copy import deepcopy
from time import time


class Base(ABC):

    name = ""  # name of algorithm (string)

    def __init__(self, initial_queue, print_result=True, print_queue=False):
        # initial_queue is PathSeries object
        # print_result is boolean, default is True
        # print_queue is boolean, default is False
        self.initial_queue = initial_queue
        self.print_result = print_result
        self.print_queue = print_queue
        self.path_to_goal = None
        self.goal_is_reached = False
        self.queue_lengths = [len(self.initial_queue)]
        self.elapsed_time = None
        self.nr_iterations = 0

    def _initialize(self):
        # initialize attributes
        # called by constructor and by method search
        self.path_to_goal = None
        self.goal_is_reached = False
        self.queue_lengths = [len(self.initial_queue)]
        self.elapsed_time = None
        self.nr_iterations = 0

    @abstractmethod
    def search(self):
        pass

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
            print('Maximum length of queue:', max(self.queue_lengths))

    def __repr__(self):
        # overrides inherited __repr__ method
        # returns string
        return self.name


class Algorithm(Base):

    def __init__(self, initial_queue, print_result=True, print_queue=False):
        # initial_queue is PathSeries object
        # print_result is boolean, default is True
        # print_queue is boolean, default is False
        super().__init__(initial_queue, print_result, print_queue)

    def _initialize(self):
        # initialize attributes
        # called by method search
        super()._initialize()
        self._queue = deepcopy(self.initial_queue)
        self._queue_class = type(self.initial_queue)
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
            self.queue_lengths.append(len(self._queue))

            # remove the first path from the queue
            self._remove_path_from_queue()

            # create new paths (to all children)
            # reject the new paths with loops
            self._create_new_paths()

            # add the new paths to the queue
            self._add_new_paths_to_queue()

            # print queue
            self._print_queue()

            # update goal_is_reached
            self._check_goal_is_reached()

        # elapsed time
        self.elapsed_time = time() - starttime

        # print path to goal
        self._print_path_to_goal()

        # print result
        self._print_result()

    def _remove_path_from_queue(self):
        # removes first path from queue
        self._first_path = self._queue.pop(0)

    def _create_new_paths(self):
        # creates new paths to all children of first path
        # rejects the new paths with loops
        self._new_paths = self._queue_class([path for path in self._first_path.calculate_children()
                                             if not path.has_loop()])

    @abstractmethod
    def _add_new_paths_to_queue(self):
        pass

    def _check_goal_is_reached(self):
        # updates goal_is_reached
        for path in self._new_paths:
            if path.reaches_goal():
                self.goal_is_reached = True
                self.path_to_goal = path
                break

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
