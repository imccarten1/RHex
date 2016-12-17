"""
Monte Carlo tree search reverse hex player with poolRAVE
by Isabel McCarten
starter code from Mopyhex at https://github.com/yotomyoto/mopyhex
"""
from rave_mctsagent import *

class PoolraveMctsagent(RaveMctsagent):
  
  def __init__(self, state=Gamestate(8)):
    super().__init__(state)
    self.black_rave = {}
    self.white_rave = {} 
  
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
    """Simulate a random game except that we play all known critical
    cells first, return the winning player and record critical cells at the end.
    """
    moves = state.moves()
    black_rave_moves = sorted(self.black_rave.keys(),
                              key=lambda cell: self.black_rave[cell])
    white_rave_moves = sorted(self.white_rave.keys(),
                              key=lambda cell: self.white_rave[cell])
    black_pool = []
    white_pool = []
    i = 0
    while len(black_pool) < 10 and i < len(black_rave_moves):
      if black_rave_moves[i] in moves:
        black_pool.append(black_rave_moves[i])
      i += 1
      
    i = 0
    while len(white_pool) < 10 and i < len(white_rave_moves):
      if white_rave_moves[i] in moves:
        white_pool.append(white_rave_moves[i])
      i += 1
    num_pool = 0
    while(state.winner() == Gamestate.PLAYERS["none"]):
      move = None
      if len(black_pool) > 0 and state.turn() == Gamestate.PLAYERS["black"]:
        move = random.choice(black_pool)
        num_pool += 1
      elif len(white_pool) > 0:
        move = random.choice(white_pool)
        num_pool += 1
      if random.random() > 0.5 or not move or move not in moves:
        move = random.choice(moves)
        num_pool -= 1
      state.play(move)
      moves.remove(move)

    black_rave_pts = []
    white_rave_pts = []

    for x in range(state.size):
      for y in range(state.size):
        if state.board[(x, y)] == Gamestate.PLAYERS["black"]:
          black_rave_pts.append((x, y))
          if state.winner() == Gamestate.PLAYERS["black"]:
            if (x, y) in self.black_rave:
              self.black_rave[(x, y)] += 1
            else:
              self.black_rave[(x, y)] = 1
          else:
            if (x, y) in self.black_rave:
              self.black_rave[(x, y)] -= 1
            else:
              self.black_rave[(x, y)] = -1
        elif state.board[(x, y)] == Gamestate.PLAYERS["white"]:
          white_rave_pts.append((x, y))
          if state.winner() == Gamestate.PLAYERS["white"]:
            if (x, y) in self.white_rave:
              self.white_rave[(x, y)] += 1
            else:
              self.white_rave[(x, y)] = 1
          else:
            if (x, y) in self.white_rave:
              self.white_rave[(x, y)] -= 1
            else:
              self.white_rave[(x, y)] = -1

    return state.winner(), black_rave_pts, white_rave_pts