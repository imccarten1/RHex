class Unionfind:
  """
  Unionfind data structure specialized for finding hex connections.
  Implementation inspired by UAlberta CMPUT 275 2015 class notes.
  """
  
  def __init__(self):
    """
    Initialize parent and rank as empty dictionarys, we will
    lazily add items as nessesary.
    """
    self.parent = {}
    self.rank = {}
    self.groups = {}
    self.ignored = []

  def join(self, x, y):
    """
    Merge the groups of x and y if they were not already,
    return False if they were already merged, true otherwise
    """
    rep_x = self.find(x)
    rep_y = self.find(y)

    if rep_x == rep_y:
      return False
    if self.rank[rep_x] < self.rank[rep_y]:
      self.parent[rep_x] = rep_y
      
      self.groups[rep_y].extend(self.groups[rep_x])
      del self.groups[rep_x]
    elif self.rank[rep_x] >self.rank[rep_y]:
      self.parent[rep_y] = rep_x
      
      self.groups[rep_x].extend(self.groups[rep_y])
      del self.groups[rep_y]      
    else:
      self.parent[rep_x] = rep_y
      self.rank[rep_y] += 1
      
      self.groups[rep_y].extend(self.groups[rep_x])
      del self.groups[rep_x]  
    
    return True

  def find(self, x):
    """
    Get the representative element associated with the set in
    which element x resides. Uses grandparent compression to compression
    the tree on each find operation so that future find operations are faster.
    """
    if x not in self.parent:
      self.parent[x] = x
      self.rank[x] = 0
      if x in self.ignored:
        self.groups[x] = []
      else:
        self.groups[x] = [x]

    px = self.parent[x]
    if x == px: return x

    gx = self.parent[px]
    if gx==px: return px

    self.parent[x] = gx

    return self.find(gx)

  def connected(self, x, y):
    """Check if two elements are in the same group."""
    return self.find(x)==self.find(y)
  
  def set_ignored_elements(self, ignore):
    """Set elements in ignored."""
    self.ignored = ignore
  
  def get_groups(self):
    """Return dictionary of groups of connected cells."""
    return self.groups
