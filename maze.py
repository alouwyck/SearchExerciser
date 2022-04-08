import state_space
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors
from time import sleep
from IPython.display import clear_output


class Position:
    # class to define maze position (irow, icol)

    def __init__(self, irow, icol):
        # irow is row index (int)
        # icol is column index (int)
        self.irow = irow
        self.icol = icol

    def __eq__(self, other):
        # compares position self to other position
        # two positions are the same if their coordinates are the same
        # returns boolean
        return self.irow == other.irow and self.icol == other.icol

    def __repr__(self):
        # overrides inherited __repr__ method
        # returns string (irow, icol)
        return f"({self.irow}, {self.icol})"


class Maze:
    # class to define maze grid

    symbols = ('*', '.', '#', 'o')  # start = *, free = ., wall = #, goal = o

    def __init__(self, grid):
        # grid is an integer array: start = 0, free = 1, wall = 2, goal = 3
        # size is the number of rows which is equal to the number of columns
        self.grid = np.array(grid, dtype=int)
        self.size = self.grid.shape[0]

    def get_start_position(self):
        # gets start position
        # returns Position object
        irow, icol = np.where(self.grid == 0)
        return Position(irow[0], icol[0])

    def get_goal_position(self):
        # gets goal position
        # returns Position object
        irow, icol = np.where(self.grid == 3)
        return Position(irow[0], icol[0])

    def is_valid_position(self, position):
        # checks if position is valid: must be inside the grid and may not coincide with wall
        # position is Position object
        # returns boolean
        return (0 <= position.irow < self.size and
                0 <= position.icol < self.size and
                self.grid[position.irow, position.icol] != 2)

    def plot(self):
        # plots maze
        cmap = colors.ListedColormap(['forestgreen', 'lightyellow', 'purple', 'red'])  # colormap
        bounds = np.linspace(-0.5, 3.5, 5)
        norm = colors.BoundaryNorm(bounds, cmap.N)
        # plot grid
        plt.matshow(self.grid, cmap=cmap, norm=norm)
        # axes
        xmax = self.size - 0.5
        ymax = self.size - 0.5
        ax = plt.gca()
        ax.set_aspect("equal")
        ax.set_xticks(np.linspace(-0.5, xmax, self.size + 1))
        ax.set_xticklabels([])
        ax.set_yticks(np.linspace(-0.5, ymax, self.size + 1))
        ax.set_yticklabels([])
        ax.tick_params(axis=u'both', which=u'both', length=0)
        # plot grid and set axis limits
        plt.grid()
        plt.xlim([-0.5, xmax])
        plt.ylim([ymax, -0.5])

    def search(self, Method, rules=None, print_result=True, print_queue=False):
        # searches path from start to goal position
        # Method is search.Algorithm class
        # rules is list of MazeProductionRule objects, default is [Left(), Right(), Up(), Down()]
        # print_result is boolean, default is True
        # print_queue is boolean, default is False
        initial_state = State(self, self.get_start_position(), rules)
        initial_path = Path([initial_state])
        method = Method(PathSeries([initial_path]), print_result=print_result, print_queue=print_queue)
        method.search()
        return method.path_to_goal

    def __repr__(self):
        # overrides inherited __repr__ method
        # returns string
        return "\n".join([''.join([self.symbols[item] for item in row]) for row in self.grid])

    @staticmethod
    def create(maze):
        # creates Maze object
        # maze is list of strings: start = '*', free = '.', wall = '#', goal = 'o'
        return Maze(grid=[[Maze.symbols.index(symbol) for symbol in row] for row in maze])

    @staticmethod
    def create_random(size, num_of_walls, seed=None):
        # creates Maze object randomly
        # size is size of maze
        # num_of_walls is number of randomly chosen walls in maze (int)
        # seed is random seed for numpy.random.choice function (int)
        maze = np.ones((size, size))  # free
        maze[0, 0] = 0  # start
        maze[-1, -1] = 3  # goal
        if seed is not None:  # set seed
            np.random.seed(seed)
        i = np.random.choice(np.arange(1, size ** 2 - 1), num_of_walls, replace=False)  # wall indices
        irow, icol = np.unravel_index(i, maze.shape)  # wall coordinates
        maze[irow, icol] = 2  # wall
        return Maze(maze)


class ProductionRule(state_space.ProductionRule):
    # class to define maze production rule: left, right, up, down
    # inherits from state_space.ProductionRule

    def __init__(self, drow=0, dcol=0):
        # drow is -1, 0, or 1 (int)
        # dcol is -1, 0, or 1 (int)
        # new position is (irow+drow, icol+dcol)
        #   left:  drow=0,  dcol=-1
        #   right: drow=0,  dcol=1
        #   up:    drow=-1, dcol=0
        #   down:  drow=1,  dcol=0
        super().__init__()
        self.drow = drow
        self.dcol = dcol

    def __repr__(self):
        # overrides inherited __repr__ method
        # returns string 'L', 'R', 'U', or 'D'
        if self.dcol == -1:
            return 'L'
        if self.dcol == 1:
            return 'R'
        if self.drow == -1:
            return 'U'
        if self.drow == 1:
            return 'D'


class Left(ProductionRule):
    # subclass that defines maze production rule 'left'
    # inherits from ProductionRule

    def __init__(self):
        super().__init__(0, -1)


class Right(ProductionRule):
    # subclass that defines maze production rule 'right'
    # inherits from ProductionRule

    def __init__(self):
        super().__init__(0, 1)


class Up(ProductionRule):
    # subclass that defines maze production rule 'up'
    # inherits from ProductionRule

    def __init__(self):
        super().__init__(-1, 0)


class Down(ProductionRule):
    # subclass that defines maze production rule 'down'
    # inherits from ProductionRule

    def __init__(self):
        super().__init__(1, 0)


class Move(state_space.Move):
    # class to define a maze move
    # inherits from state_space.Move

    def __init__(self, state, rule):
        # state is MazeState object
        # rule is MazeProductionRule object
        super().__init__(state, rule)

    def __repr__(self):
        # overrides inherited __repr__ method
        # returns string 'L', 'R', 'U', or 'D'
        return str(self.rule)


class State(state_space.State):
    # class to define maze state
    # inherits from state_space.State

    def __init__(self, maze, position, rules=None):
        # maze is a Maze object
        # position is a Position object
        # rules is a list of MazeProductionRule objects, default is [Left(), Right(), Up(), Down()]
        super().__init__([Left(), Right(), Up(), Down()] if rules is None else rules)
        self.maze = maze
        self.position = position

    def is_valid_move(self, move):
        # checks if given move is valid
        # move is Move object
        # returns boolean
        new_position = Position(self.position.irow + move.rule.drow,
                                self.position.icol + move.rule.dcol)
        return self.maze.is_valid_position(new_position)

    def apply_move(self, move):
        # applies move to state self to get new state
        # move is Move object
        # returns new MazeState object
        new_position = Position(self.position.irow + move.rule.drow,
                                self.position.icol + move.rule.dcol)
        return State(self.maze, new_position, self.rules)  # new state

    def is_goal(self):
        # checks if state self is a goal state
        # returns boolean
        return self.maze.get_goal_position() == self.position

    def __eq__(self, other):
        # overrides inherited __eq__ method
        # checks if state self is equal to other state
        # two states are the same if their positions are the same
        # returns boolean
        return self.position == other.position

    def __repr__(self):
        # overrides inherited __repr__ method
        # returns string with position coordinate
        return str(self.position)


class Path(state_space.Path):
    # class to define maze path
    # inherits from state_space.Path

    def __init__(self, states):
        # states is list of MazeState objects
        super().__init__(states)

    def plot(self):
        # plots path in maze
        self[-1].maze.plot()
        x = np.arange(0, self[-1].maze.grid.size)
        plt.plot(x[self[-1].position.icol], x[self[-1].position.irow], 'bo')
        positions = [state.position for state in self[:-1]]
        irow = np.array([position.irow for position in positions])
        icol = np.array([position.icol for position in positions])
        if len(positions) > 0:
            plt.plot(x[icol], x[irow], 'ko')

    def plot_live(self, wait=0.5):
        # plots live path in maze
        x = np.arange(0, self[-1].maze.grid.size)
        icol, irow = [], []
        for position in [state.position for state in self]:
            self[-1].maze.plot()
            irow.append(position.irow)
            icol.append(position.icol)
            plt.plot(x[icol], x[irow], 'ko')
            plt.show()
            sleep(wait)
            clear_output()
        self.plot()

    def __repr__(self):
        # overrides inherited __repr__ method
        # returns string
        maze = np.array([list(row) for row in str(self[-1].maze).split('\n')])
        for position in [state.position for state in self]:
            maze[position.irow][position.icol] = "x"
        return "\n".join(["".join(row) for row in maze])


class PathSeries(state_space.PathSeries):
    # class to define series of maze paths
    # inherits from state_space.PathSeries

    def __init__(self, paths):
        # paths is list of MazePath objects
        super().__init__(paths)

    def __repr__(self):
        # overrides inherited __repr__ method
        # returns string
        if len(self) > 0:
            lst = [np.array([list(row) for row in str(path).split('\n')]) for path in self]
            arr = np.hstack([np.hstack((a, np.repeat([[' ', ' ']], a.shape[0], axis=0))) for a in lst])
            return '\n'.join([''.join(row) for row in arr])
        else:
            return ""
