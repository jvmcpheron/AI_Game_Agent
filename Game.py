class State:
    """A state has the player to move, a cached utility, a list of moves
    in the form of a list of (x, y) positions, and a board, in the
    form of a dict of {(x, y): Player} entries, where Player is 'X' or
    'O'.  We also store a "winning move" for winning states which contains
    the position where the win was made. 
    """
    def __init__(self,to_move,utility,board,moves,winning_move=None):
        self.to_move = to_move
        self.utility = utility
        self.board = board
        self.moves = moves
        self.winning_move = winning_move

    def __eq__(self,other):
        return self.board == other.board
    
    def __hash__(self):
        return hash(str(self.board))

class Game:
    """A game is similar to a problem, but it has a utility for each
    state and a terminal test instead of a path cost and a goal
    test. To create a game, subclass this class and implement
    legal_moves, make_move, utility, and terminal_test. You may
    override display and successors or you can inherit their default
    methods. You will also need to set the .initial attribute to the
    initial state; this can be done in the constructor."""

    def legal_moves(self, state):
        "Return a list of the allowable moves at this point."
        abstract

    def make_move(self, move, state):
        "Return the state that results from making a move from a state."
        abstract
            
    def utility(self, state, player):
        "Return the value of this final state to player."
        abstract

    def terminal_test(self, state):
        "Return True if this is a final state for the game."
        return not self.legal_moves(state)

    def to_move(self, state):
        "Return the player whose move it is in this state."
        return state.to_move

    def display(self, state):
        "Print or otherwise display the state."
        print(state)

    def successors(self, state):
        "Return a list of legal (move, state) pairs."
        return [(move, self.make_move(move, state))
                for move in self.legal_moves(state)]

    def __repr__(self):
        return '<%s>' % self.__class__.__name__

class TicTacToe(Game):
    """Play TicTacToe on an h x v board, with Max (first player) playing 'X'."""
    def __init__(self, h=3, v=3, k=3):
        self.h=h
        self.v=v
        self.k=k
        moves = [(x, y) for x in range(1, h+1)
                 for y in range(1, v+1)]
        self.initial = State(to_move='X', utility=0, board={}, moves=moves)

    def legal_moves(self, state):
        "Legal moves are any square not yet taken."
        return state.moves

    def make_move(self, move, state):
        if move not in state.moves:
            return state # Illegal move has no effect
        board = state.board.copy(); board[move] = state.to_move
        moves = list(state.moves); moves.remove(move)
        utility = self.compute_utility(board, move, state.to_move)
        return State(to_move='O' if state.to_move == 'X' else 'X',
                      utility=utility, board=board, moves=moves,
                     winning_move=move if utility != 0 else None)

    def utility(self, state, player):
        "Return the value to X; 1 for win, -1 for loss, 0 otherwise."
        return state.utility

    def terminal_test(self, state):
        "A state is terminal if it is won or there are no empty squares."
        return state.utility != 0 or len(state.moves) == 0

    def display(self, state):
        board = state.board
        for x in range(1, self.h+1):
            for y in range(1, self.v+1):
                print(board.get((x, y), '.'),end='')
            print('')

    def compute_utility(self, board, move, player):
        "If X wins with this move, return 1; if O return -1; else return 0."
        if len(self.k_in_row(board, move, player, (0, 1))) >= self.k: return 1 if player == 'X' else -1
        if len(self.k_in_row(board, move, player, (1, 0))) >= self.k: return 1 if player == 'X' else -1
        if len(self.k_in_row(board, move, player, (1, -1))) >= self.k: return 1 if player == 'X' else -1
        if len(self.k_in_row(board, move, player, (1, 1))) >= self.k: return 1 if player == 'X' else -1
        else:
            return 0

    def k_in_row(self, board, move, player, delta):
        """If there is a line of k through move on board for player, return
        it. Otherwise, return empty list
        """
        x, y = move
        delta_x, delta_y = delta
        line = set()
        while board.get((x, y)) == player:
            line.add((x,y))
            x, y = x + delta_x, y + delta_y
        x, y = move
        while board.get((x, y)) == player:
            line.add((x,y))
            x, y = x - delta_x, y - delta_y
        if len(line) >= self.k: return list(line)
        else: return []

class ConnectFour(TicTacToe):
    """A TicTacToe-like game in which you can only make a move on the bottom
    row, or in a square directly above an occupied square.  Traditionally
    played on a 7x6 board and requiring 4 in a row."""
    
    def __init__(self, h=7, v=6, k=4):
        TicTacToe.__init__(self, h, v, k)

    def legal_moves(self, state):
        "Legal moves are any square not yet taken."
        return [(x, y) for (x, y) in state.moves
                if y == self.v or (x, y+1) in state.board]

