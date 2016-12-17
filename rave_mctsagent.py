"""
Monte Carlo tree search reverse hex player
starter code from Mopyhex at https://github.com/yotomyoto/mopyhex
"""
from mctsagent import *
from gamestate import Gamestate

class Rave_Node(Node):
  
  def __init__(self, move = None, parent = None):
    """
    Initialize a new node with optional move and parent and initially empty
    children list and rollout statistics and unspecified outcome.
    """
    self.move = move
    self.parent = parent
    self.N = 0 #times this position was visited
    self.Q = 0 #average reward (wins-losses) from this position
    self.Q_RAVE = 0 # times this move has been critical in a rollout
    self.N_RAVE = 0 # times this move has appeared in a rollout
    self.children = {}
    self.outcome = Gamestate.PLAYERS["none"]

  def add_children(self, children):
    for child in children:
      self.children[child.move] = child

  def value(self, explore, crit):
    """
    Calculate the UCT value of this node relative to its parent, the parameter
    "explore" specifies how much the value should favor nodes that have
    yet to be thoroughly explored versus nodes that seem to have a high win
    rate. 
    Currently explore is set to zero when choosing the best move to play so
    that the move with the highest winrate is always chossen. When searching
    explore is set to EXPLORATION specified above.
    """
    #unless explore is set to zero, maximally favor unexplored nodes
    if(self.N == 0):
      if(explore == 0):
        return 0
      else:
        return inf
    else:
      #rave valuation:
      alpha = max(0,(crit - self.N)/crit)
      return self.Q*(1-alpha)/self.N+self.Q_RAVE*alpha/self.N_RAVE


class RaveMctsagent(Mctsagent):
  RAVE_CONSTANT = 300
  EXPLORATION = 1
  
  CASES = {}
  CASE_FIRST = {}
  CASE_SINGLE = {}

  CASES[2] = {(0, 1): (1, 1), (1, 1): (0, 1)}
  CASE_FIRST[2] = [(0, 0)]
  CASE_SINGLE[2] = (1, 0)

  CASES[3] = {(0, 1): (0, 2), (0, 2): (0, 1), (2, 0): (2, 1), (2, 1): (2, 0)}
  CASE_FIRST[3] = [(0, 0), (1, 0), (1, 2), (2, 2)]
  CASE_SINGLE[3] = (1, 1)

  CASES[4] = {(2, 0): (3, 0), (3, 0): (2, 0), (2, 2): (3, 1), (3, 1): (2, 2),
              (1, 2): (3, 2), (3, 2): (1, 2), (0, 3): (1, 3), (1, 3): (0, 3),
              (2, 3): (3, 3), (3, 3): (2, 3)}
  CASE_FIRST[4] = [(0, 0), (1, 0), (0, 1), (0, 2), (1, 1)]
  CASE_SINGLE[4] = (2, 1)

  CASES[5] = {(0, 1): (0, 2), (0, 2): (0, 1), (0, 3): (0, 4), (0, 4): (0, 3),
              (1, 1): (1, 3), (1, 3): (1, 1), (1, 2): (2, 1), (2, 1): (1, 2),
              (3, 1): (3, 3), (3, 3): (3, 1), (2, 3): (3, 2), (3, 2): (2, 3),
              (4, 0): (4, 1), (4, 1): (4, 0), (4, 2): (4, 3),(4, 3): (4, 2)}
  CASE_FIRST[5] = [(0, 0), (1, 0), (2, 0), (3, 0), (1, 4), (2, 4), (3, 4),
                   (4, 4)]
  CASE_SINGLE[5] = (2, 2)  
  
  def __init__(self, state=Gamestate(8)):
    self.set_gamestate(state)
    self.short_symetrical = True
  
  def special_case(self, last_move):
    """Return a move found without search, None otherwise."""
    return None

  def best_move(self):
    """
    Return the best move according to the current tree.
    """
    if(self.rootstate.winner() != Gamestate.PLAYERS["none"]):
      return gamestate.GAMEOVER

    #choose the move of the most simulated node breaking ties randomly
    max_value = max(self.root.children.values(), key = lambda n: n.N).N
    max_nodes = [n for n in self.root.children.values() if n.N == max_value]
    bestchild = random.choice(max_nodes)
    return bestchild.move

  def move(self, move):
    """
    Make the passed move and update the tree approriately.
    """
    if move in self.root.children:
      child = self.root.children[move]
      child.parent = None
      self.root = child
      self.rootstate.play(child.move)
      return

    #if for whatever reason the move is not in the children of
    #the root just throw out the tree and start over
    self.rootstate.play(move)
    self.root = Rave_Node()

  def search(self, time_budget):
    """
    Search and update the search tree for a specified amount of time
    in secounds.
    """
    startTime = time.clock()
    num_rollouts = 0

    #do until we exceed our time budget
    while(time.clock() - startTime < time_budget):
      node, state = self.select_node()
      turn = state.turn()
      outcome, black_rave_pts, white_rave_pts = self.roll_out(state)
      self.backup(node, turn, outcome, black_rave_pts, white_rave_pts)
      num_rollouts += 1

    #stderr.write("Ran "+str(num_rollouts)+ " rollouts in " +\
    #  str(time.clock() - startTime)+" sec\n")
    #stderr.write("Node count: "+str(self.tree_size())+"\n")

  def select_node(self):
    """
    Select a node in the tree to preform a single simulation from.
    """
    node = self.root
    state = deepcopy(self.rootstate)

    #stop if we reach a leaf node
    while(len(node.children) != 0):
      max_node = max(node.children.values(),
                     key=lambda n: n.value(self.EXPLORATION, self.RAVE_CONSTANT))
      
      max_value = max_node.value(self.EXPLORATION, self.RAVE_CONSTANT)
      #decend to the maximum value node, break ties at random
      max_nodes = [n for n in node.children.values() if 
                   n.value(self.EXPLORATION, self.RAVE_CONSTANT) == max_value]
      node = random.choice(max_nodes)
      state.play(node.move)

      #if some child node has not been explored select it
      #before expanding other children
      if node.N == 0:
        return (node, state)

    #if we reach a leaf node generate its children and return one of
    #them if the node is terminal, just return the terminal node
    if(self.expand(node, state)):
      node = random.choice(list(node.children.values()))
      state.play(node.move)
    return (node, state)

  def backup(self, node, turn, outcome, black_rave_pts, white_rave_pts):
    """
    Update the node statistics on the path from the passed node to
    root to reflect the outcome of a randomly simulated playout.
    """
    # note that reward is calculated for player who just played
    # at the node and not the next player to play
    reward = -1 if outcome == turn else 1

    while node != None:
      if turn == Gamestate.PLAYERS["white"]:
        for point in white_rave_pts:
          if point in node.children:
            node.children[point].Q_RAVE += -reward
            node.children[point].N_RAVE += 1
      else:
        for point in black_rave_pts:
          if point in node.children:
            node.children[point].Q_RAVE += -reward
            node.children[point].N_RAVE += 1

      node.N += 1
      node.Q += reward
      if turn == Gamestate.PLAYERS["black"]:
        turn = Gamestate.PLAYERS["white"]
      else:
        turn = Gamestate.PLAYERS["black"]
      reward = -reward
      node = node.parent

  def expand(self, parent, state):
    """
    Generate the children of the passed "parent" node based on the available
    moves in the passed gamestate and add them to the tree.
    """
    children = []
    if(state.winner() != Gamestate.PLAYERS["none"]): 
      #game is over at this node so nothing to expand
      return False

    for move in state.moves():
      children.append(Rave_Node(move, parent))

    parent.add_children(children)
    return True

  def set_gamestate(self, state):
    """
    Set the rootstate of the tree to the passed gamestate, this clears all the
    information stored in the tree since none of it applies to the new state.
    """
    self.rootstate = deepcopy(state)
    self.root = Rave_Node()

  def roll_out(self, state):
    """
    Simulate a random game except that we play all known critical
    cells first, return the winning player and record critical cells at the end.
    """
    moves = state.moves()
    
    while(state.winner() == Gamestate.PLAYERS["none"]):
      move = random.choice(moves)
      state.play(move)
      moves.remove(move)

    black_rave_pts = []
    white_rave_pts = []

    for x in range(state.size):
      for y in range(state.size):
        if state.board[(x,y)] == Gamestate.PLAYERS["black"]:
          black_rave_pts.append((x,y))
        elif state.board[(x,y)] == Gamestate.PLAYERS["white"]:
          white_rave_pts.append((x,y))

    return state.winner(), black_rave_pts, white_rave_pts

  def tree_size(self):
    """Count nodes in tree by BFS."""
    Q = Queue()
    count = 0
    Q.put(self.root)
    while not Q.empty():
      node = Q.get()
      count += 1
      for child in node.children.values():
        Q.put(child)
    return count  
  
  def get_small_board_move(self, last_move, size, moves):
    """
    Return special case moves on 5x5 or smaller boards.
    If no such move can be found return None.
    """
    turn = self.rootstate.turn()
    if not((size % 2 == 0 and turn == Gamestate.PLAYERS["white"]) or 
           (size % 2 == 1 and turn == Gamestate.PLAYERS["black"])):
      return None
    
    case = self.CASES[size]
    if last_move in case and case[last_move] in moves:
      return case[last_move]
    elif (last_move in case and case[last_move] not in moves or 
          last_move == self.CASE_SINGLE[size]):
      for key in case.keys():
        if key in moves and case[key] in moves:
          return key
    for cell in self.CASE_FIRST[size]:
      if cell in moves:
        return cell    

  def get_starting_move(self, last_move, size, moves):
    """
    Return special case moves for the start of the game.
    If no such move can be found return None.
    """
    far_corner = (size - 1, size - 1)
    
    if self.rootstate.num_played == 0 and size % 2 == 0:
      # Play in the acute corners first.
      return random.choice([(0, 0), far_corner])
    elif last_move == None:
      return None
    
    short_diagonal_reflect = (size - 1 - last_move[0], size - 1 - last_move[1])
    if self.rootstate.num_played == 1 and size % 2 == 1:
      # if the first move was not on the long diagonal
      if last_move[0] != last_move[1]:
        # Play the reflection of that move in the long diagonal
        return (last_move[1], last_move[0])
      # If the first move was the centre cell
      elif last_move[0] == (size - 1) / 2 and last_move[1] == (size - 1) / 2:
        return random.choice((0, 0), far_corner)
      else:
        # Play the reflection in short diagonal
        return short_diagonal_reflect
    # Maintain symetry with the opponents moves as long as possible.
    elif size % 2 == 1 and self.rootstate.num_played % 2 == 1:
      if self.rootstate.blank_ldiagonal():
        self.short_symetrical = False
        return (last_move[1], last_move[0])
      
      elif (self.rootstate.blank_sdiagonal() 
          and self.short_symetrical):
        return short_diagonal_reflect
      
    return None