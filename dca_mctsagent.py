"""
Monte Carlo tree search reverse hex player with dead cell ananlysis
by Isabel McCarten
starter code from Mopyhex at https://github.com/yotomyoto/mopyhex
The method for detecting dead cells is based on the one used
by benzene: https://github.com/jakubpawlewicz/benzene
"""

from rave_mctsagent import *

class DCAMctsagent(RaveMctsagent):
  
  RAVE_CONSTANT = 300

  def __init__(self, state=Gamestate(8)):
    super().__init__(state)
    self.dead = set()

  def special_case(self, last_move):
    """Return a move found without search, None otherwise."""
    size = self.rootstate.size
    moves = self.rootstate.moves()
      
    if size < 6:
      move = self.get_small_board_move(last_move, size, moves)
      if move is not None:
        return move
    
    move = self.get_starting_move(last_move, size, moves)
    if move is not None:
      return move
      
    self.findDeadRegions()
    if len(self.dead) > 0:
      move = self.dead.pop()
      return move
    
    return None
  
  def move(self, move):
    """
    Make the passed move and update the tree approriately.
    """
    self.dead.discard(move)
    super().move(move)
  
  def findEdgeUnreachable(self, color, stopset,
                          checkSide1=True, checkSide2=True):
    """
    Finds areas unreachable from either side of the board by crossing only empty
    or color cells and without crossing cells in the stopset. The calculation is
    skipped for a side if the stopset touches it, indicated by checkSide1 and
    checkSide2. 
    """
    colors = [color, Gamestate.PLAYERS["none"]]
    if checkSide1:
      reachable1 = self.rootstate.reachable(colors, stopset, Gamestate.EDGE1)
    else:
      reachable1 = set()
    if checkSide2:
      reachable2 = self.rootstate.reachable(colors, stopset, Gamestate.EDGE2)
    else:
      reachable2 = set()
    
    return self.rootstate.get_empty_cell_set() - (reachable1 | reachable2)

  def findDeadRegions(self):
    """
    Finds dead cells created by a single connected group of stones' neighbors
    and adds them to self.dead.
    """    
    color_groups = [self.rootstate.get_black_groups(),
                    self.rootstate.get_white_groups()]
    for groups in color_groups:
      for key in groups.keys():
        group = groups[key]
        if len(group) < 2:
          continue
        color = self.rootstate.get_color(group[0])
        nb = set()
        
        for cell in group:
          for neighbor in self.rootstate.neighbors(cell):
            if self.rootstate.get_color(neighbor) == Gamestate.PLAYERS["none"]:
              nb.add(neighbor)
        
        checkSide1 = True
        checkSide2 = True
        if color == Gamestate.PLAYERS["black"]:
          for cell in group:
            if cell[1] == 0:
              checkSide1 = False
            elif cell[1] == self.rootstate.size - 1:
              checkSide2 = False
        elif color == Gamestate.PLAYERS["white"]:
          for cell in group:
            if cell[0] == 0:
              checkSide1 = False
            elif cell[0] == self.rootstate.size - 1:
              checkSide2 = False
              
        self.dead = self.dead | self.findEdgeUnreachable(color, nb, checkSide1,
                                                               checkSide2)