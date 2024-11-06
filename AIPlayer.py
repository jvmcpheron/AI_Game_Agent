import random 
import math
from collections import defaultdict


## Utility to find element of seq that maximizes fn
def argmax(seq, fn):
    return seq[max(enumerate([fn(x) for x in seq]),key=lambda p:p[1])[0]]

## Choose a random legal move
def random_decision(state, game):
    return random.choice(game.legal_moves(state))

## MiniMax decision (figure 5.3)
def minimax_decision(state, game):
    player = game.to_move(state)

    def max_value(state):
        ### ... you fill this in ...
        ### Hint: you can make use of
        ###   game.terminal_test(state)
        ###   game.utility(state,player)
        ###   game.sucessors(state)

        if game.terminal_test(state):
            return game.utility(state, player)
        v = float('-inf')
        for _, successor in game.successors(state):
            v = max(v, min_value(successor))
        return v

        #PSEUDOCODE
        # if Terminal - Test(state)
        #   return Utility(state)
        # v = −∞
        # for (a, s) ∈ Successors(state)
        #   v = Max(v, Min - Value(s))
        # return v

    def min_value(state):
        ### ... you fill this in ...

        #PSEUDOCODE
        # if Terminal - Test(state)
        #   return Utility(state)
        # v = +∞
        # for (a, s) ∈ Successors(state)
        #   v = Min(v, Max - Value(s))
        # return v

        if game.terminal_test(state):
            return game.utility(state, player)
        v = float('inf')
        for _, successor in game.successors(state):
            v = min(v, max_value(successor))
        return v

        
    # Body of minimax_decision starts here:
    action, state = argmax(game.successors(state), lambda x: min_value(x[1]))
    return action

## MiniMax with Alpha-Beta pruning (figure 5.7)
def alphabeta_decision(state, game):

    player = game.to_move(state)

    def max_value(state, alpha, beta):
        ### ... you fill this in ...
        v = float('-inf')
        if game.terminal_test(state):
            return game.utility(state, player)
        for _, successor in game.successors(state):
            v = max(v, min_value(successor, alpha, beta))

            #added this code
            if v >= beta:
                return v
            alpha = max(alpha,v)
            #done
        return v

    def min_value(state, alpha, beta):
        if game.terminal_test(state):
            return game.utility(state, player)
        v = float('inf')
        for _, successor in game.successors(state):
            v = min(v, max_value(successor, alpha, beta))

            #added this code
            if v <= alpha:
                return v
            alpha = min(beta,v)
            #done

        return v

        ### ... you fill this in ...

    action, state = argmax(game.successors(state),
                           lambda x: min_value(x[1], float('-inf'), float('inf')))
    return action

## MiniMax with Alpha-Beta pruning, cutoff and evaluation (section 5.4.2)
def alphabeta_cutoff_decision(state, game, d=4):
    """Search game to determine best action; use alpha-beta pruning.
    This version cuts off search and uses an evaluation function."""

    player = game.to_move(state)

    def max_value(state, alpha, beta, depth):
        v = float('-inf')
        if game.terminal_test(state) or depth == d:
            return game.utility(state, player)
        for _, successor in game.successors(state):
            v = max(v, min_value(successor, alpha, beta, depth+1))

            if v >= beta:
                return v
            alpha = max(alpha, v)

        return v



    def min_value(state, alpha, beta, depth):

        if game.terminal_test(state) or depth == d:
            return game.utility(state, player)
        v = float('inf')
        for _, successor in game.successors(state):
            v = min(v, max_value(successor, alpha, beta, depth+1))

            if v <= alpha:
                return v
            alpha = min(beta, v)

        return v

    ## ... fill in any logic for cutoff test and eval ... ????

    action, state = argmax(game.successors(state),
                           lambda x: min_value(x[1], float('-inf'), float('inf'), 0))
    return action



## Simulate a game starting at state, returning utility
## Uses a random playout policy
def simulate(state, game):
    while True:
        if game.terminal_test(state):
            return game.utility(state,game.to_move(state))            
        a,s  = random.choice(game.successors(state))
        state = game.make_move(a,state)
    
def pure_mc_decision(state, game, nplayouts=10):
    score = dict()
    for a,s in game.successors(state):
        score[a] = 0
        for _ in range(nplayouts):
            score[a] += simulate(s,game)
    return max(score, key=score.get)

class MCTS_Node:
    def __init__(self,state,parent=None):
        self.state = state        
        self.parent=parent
        self.children = []
        
## Monte Carlo Tree Search (fig 5.11 on page 163)
def mcts_decision(state, game, nplayouts=10):
    tree = MCTS_Node(state)
    # A dictionary that maps states to playout count
    N = defaultdict(int)
    # A dictionary that maps states to total playout utility
    U = defaultdict(int)


    #code to get UCT score
    def uct_score(child, total_visits, exploration_param=1.414):
        if N[state] == 0:
            return float('inf')  # Favor unexplored nodes

        #calculate value of node
        exploit = U[state] / N[state]

        #don't just wanna exploit (wanna try new moves too)
        explore = exploration_param * math.sqrt(math.log(total_visits) / N[state])


        return exploit + explore

    ## Find a leaf of tree using UCT selection policy
    def select(node):
        ## ... you fill this in ...

        #PSEUDOCODE
        # if node is a leaf or corresponds to a terminal state
        #   return node
        # S = children of node
        # return Select(arg maxn∈S UCT(n))

        # while the node has children (not a leaf)
        while node.children:
            node = max(node.children, key=lambda child: uct_score(child.state, N[node.state]))

        #return when we reach a leaf
        return node

        
    ## Grow the search tree by generating children of this node
    def expand(node):
        ## ... you fill this in ...
        if game.terminal_test(node.state):
            return node

        #generate successorsss
        for move, new_state in game.successors(node.state):


            if not any(child.state == new_state for child in node.children):
                child_node = MCTS_Node(new_state, parent=node)

                #add child
                node.children.append(child_node)


        return random.choice(node.children)
        
    ## send reward back up the tree
    def backpropagate(result,node):
        ## ... you fill this in ...
        while node:

            thisState = node.state

            #update dictionaries
            N[thisState] = N[thisState] + 1
            U[thisState] = U[thisState] + result

            #move up tree
            node = node.parent

    for _ in range(nplayouts):
        leaf = select(tree)
        child = expand(leaf)
        result = simulate(child.state,game)
        backpropagate(result,child)

    moves = game.successors(state)
    score = [U[s]/N[s] if N[s] != 0 else float('-inf') for a,s in moves]
    maxindex = max(enumerate(score),key=lambda x:x[1])[0]

    ## return the move from state with best relative score
    return moves[maxindex][0]


