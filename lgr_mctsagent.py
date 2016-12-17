"""
Monte Carlo tree search reverse hex player 
with last good reply simulation policy
by Isabel McCarten
starter code from Mopyhex at https://github.com/yotomyoto/mopyhex
"""
from rave_mctsagent import *


class LGRMctsagent(RaveMctsagent):
  
  def __init__(self, state=Gamestate(8)):
    super().__init__(state)
    self.black_reply = {}
    self.white_reply = {}
  
  def special_case(self, last_move):
    """Return a move found without search, None otherwise."""
    size = self.rootstate.size
    moves = self.rootstate.moves()
    
    if size < 6:
      move = self.get_small_board_move(last_move, size, moves)
      if move is not None:
        return move
    
    move = self.get_starting_move(last_move, size, moves)
    return move    

  def roll_out(self, state):
    """
    Simulate a random game except that we play all known critical cells first,
    return the winning player and record critical cells at the end.
    """
    moves = state.moves()
    first = state.turn()
    if first == Gamestate.PLAYERS["black"]:
      current_reply = self.black_reply
      other_reply = self.white_reply
    else:
      current_reply = self.white_reply
      other_reply = self.black_reply
    black_moves = []
    white_moves = []
    last_move = None
    while(state.winner() == Gamestate.PLAYERS["none"]):
      if last_move in current_reply:
        move = current_reply[last_move]
        if move not in moves or random.random() > 0.5:
          move = random.choice(moves)
      else:
        move = random.choice(moves)
      if state.turn() == Gamestate.PLAYERS["black"]:
        black_moves.append(move)
      else:
        white_moves.append(move)
      current_reply, other_reply = other_reply, current_reply
      state.play(move)
      moves.remove(move)
      last_move = move

    black_rave_pts = []
    white_rave_pts = []

    for x in range(state.size):
      for y in range(state.size):
        if state.board[(x,y)] == Gamestate.PLAYERS["black"]:
          black_rave_pts.append((x,y))
        elif state.board[(x,y)] == Gamestate.PLAYERS["white"]:
          white_rave_pts.append((x,y))
    
    offset = 0
    skip = 0          
    if state.winner() == Gamestate.PLAYERS["black"]:
      
      if first == Gamestate.PLAYERS["black"]:
        offset = 1
      if state.turn() == Gamestate.PLAYERS["black"]:
        skip = 1
      for i in range(len(white_moves) - skip):
        self.black_reply[white_moves[i]] = black_moves[i + offset]
    else:
      if first == Gamestate.PLAYERS["white"]:
        offset = 1
      if state.turn() == Gamestate.PLAYERS["white"]:
        skip = 1
      for i in range(len(black_moves) - skip):
        self.white_reply[black_moves[i]] = white_moves[i + offset]

    return state.winner(), black_rave_pts, white_rave_pts
  
  def set_gamestate(self, state):
    """
    Set the rootstate of the tree to the passed gamestate, this clears all the
    information stored in the tree since none of it applies to the new state.
    """
    super().set_gamestate(state)
    self.white_reply = {}
    self.black_reply = {}  



