"""
Monte Carlo tree search reverse hex player with decisive move simulation policy
by Isabel McCarten
starter code from Mopyhex at https://github.com/yotomyoto/mopyhex
"""
from rave_mctsagent import *


class DecisiveMoveMctsagent(RaveMctsagent):
  
  def __init__(self, state=Gamestate(8)):
    super().__init__(state)
  
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
    Simulate a random game except that we play all known critical cells
    first, return the winning player and record critical cells at the end.
    """
    moves = state.moves()
    good_moves = moves.copy()
    good_opponent_moves = moves.copy()
    to_play = state.turn()
    
    while(state.winner() == Gamestate.PLAYERS["none"]):
      done = False
      while len(good_moves) > 0 and not done:
        move = random.choice(good_moves)
        good_moves.remove(move)
        if not state.would_lose(move, to_play):
          state.play(move)
          moves.remove(move)
          if move in good_opponent_moves:
            good_opponent_moves.remove(move)
          done = True
      
      if not done:    
        move = random.choice(moves)
        state.play(move)
        moves.remove(move)
        if move in good_opponent_moves:
          good_opponent_moves.remove(move)
          
      good_moves, good_opponent_moves = good_opponent_moves, good_moves
    
    black_rave_pts = []
    white_rave_pts = []

    for x in range(state.size):
      for y in range(state.size):
        if state.board[(x,y)] == Gamestate.PLAYERS["black"]:
          black_rave_pts.append((x,y))
        elif state.board[(x,y)] == Gamestate.PLAYERS["white"]:
          white_rave_pts.append((x,y))

    return state.winner(), black_rave_pts, white_rave_pts