from .base import Algorithm


class HeuristicSearch(Algorithm):

    def __init__(self, initial_queue, heuristic, print_result=True, print_queue=False):
        super().__init__(initial_queue, print_result, print_queue)
        self.heuristic = heuristic


class HC(HeuristicSearch):
    # class that implements hill climbing

    name = 'Hill Climbing'

    def __init__(self, initial_queue, heuristic, print_result=True, print_queue=False):
        super().__init__(initial_queue, heuristic, print_result, print_queue)

    def _add_new_paths_to_queue(self):
        # sorts the new paths using heuristic f
        # adds the sorted new paths to the front of the queue
        self._new_paths = sorted(self._new_paths, key=lambda path: self.heuristic(path.last_state()))
        super()._add_new_paths_to_queue()


class GS(HeuristicSearch):
    # class that implements greedy search

    name = "Greedy search"

    def __init__(self, initial_queue, heuristic, print_result=True, print_queue=False):
        super().__init__(initial_queue, heuristic, print_result, print_queue)

    def _add_new_paths_to_queue(self):
        # adds the new paths to the front of the queue
        # sorts the entire queue using heuristic f
        super()._add_new_paths_to_queue()
        self._queue = sorted(self._queue, key=lambda path: self.heuristic(path.last_state()))

