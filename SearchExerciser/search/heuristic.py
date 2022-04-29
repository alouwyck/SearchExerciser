from .blind import DFS
from time import time


class HC(DFS):
    # class that implements hill climbing

    name = "Hill Climbing 1 (DFS)"

    def __init__(self, initial_queue, heuristic=None, print_result=True, print_queue=False):
        super().__init__(initial_queue, print_result, print_queue)
        self.heuristic = heuristic

    def search(self):
        # performs the implemented search algorithm

        # start time
        start_time = time()

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

                # sort the new paths using heuristic f
                self._new_paths = sorted(self._new_paths, key=lambda path: self.heuristic(path.last_state()))

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
        self.elapsed_time = time() - start_time

        # print path to goal
        self._print_path_to_goal()

        # print result
        self._print_result()


class GS(DFS):
    # class that implements greedy search

    name = "Greedy search"

    def __init__(self, initial_queue, heuristic=None, print_result=True, print_queue=False):
        super().__init__(initial_queue, print_result, print_queue)
        self.heuristic = heuristic

    def search(self):
        # performs the implemented search algorithm

        # start time
        start_time = time()

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

                # sort the entire queue using heuristic f
                self._queue = sorted(self._queue, key=lambda path: self.heuristic(path.last_state()))

                # print queue
                self._print_queue()

                # update goal_is_reached
                for path in self._new_paths:
                    if path.reaches_goal():
                        self.goal_is_reached = True
                        self.path_to_goal = path
                        break

        # elapsed time
        self.elapsed_time = time() - start_time

        # print path to goal
        self._print_path_to_goal()

        # print result
        self._print_result()
