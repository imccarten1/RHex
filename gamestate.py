import numpy as np
from unionfind import unionfind
from collections import deque

class gamestate:
	"""
	Stores information representing the current state of a game of hex, namely
	the board and the current turn. Also provides functions for playing the game
	and returning information about it.
	"""
	#dictionary associating numbers with players for book keeping
	PLAYERS = {"none" : 0, "white" : 1, "black" : 2}
	OPPONENT ={0 : 0, 1 : 2, 2 : 1}
	DARK_STATE = {"unknown" : 0, "visible" : 1}

	#move value of -1 indicates the game has ended so no move is possible
	GAMEOVER = -1 

	#represent edges in the union find strucure for win detection
	EDGE1 = 1
	EDGE2 = 2
	
	DISP_WHITE = 'O'
	DISP_BLACK = '@'
	DISP_EMPTY = '.'
		

	neighbor_patterns = ((-1,0), (0,-1), (-1,1), (0,1), (1,0), (1,-1))

	def __init__(self, size):
		"""
		Initialize the game board and give white first turn.
		Also create our union find structures for win checking.
		"""
		self.size = size
		self.toplay = self.PLAYERS["white"]
		self.board = np.zeros((size, size))
		self.revealed = np.zeros((size, size))
		self.white_groups = unionfind()
		self.black_groups = unionfind()
		self.white_groups.set_ignored_elements([self.EDGE1, self.EDGE2])
		self.black_groups.set_ignored_elements([self.EDGE1, self.EDGE2])
		self.num_played = 0
		self.empty = set()
		for i in range(self.size):
			for j in range(self.size):
				self.empty.add((i, j))
				
	def get_white_groups(self):
		return self.white_groups.get_groups()
	
	def get_black_groups(self):
		return self.black_groups.get_groups()

	def play(self, cell):
		"""
		Play a stone of the current turns color in the passed cell.
		"""
		if(self.toplay == self.PLAYERS["white"]):
			self.place_white(cell)
			self.toplay = self.PLAYERS["black"]
		elif(self.toplay == self.PLAYERS["black"]):
			self.place_black(cell)
			self.toplay = self.PLAYERS["white"]
		self.num_played += 1

	def place_white(self, cell):
		"""
		Place a white stone regardless of whose turn it is.
		"""
		if(self.board[cell] == self.PLAYERS["none"]):
			self.board[cell] = self.PLAYERS["white"]
			self.empty.remove(cell)
		else:
			raise ValueError("Cell occupied")
		#if the placed cell touches a white edge connect it appropriately
		if(cell[0] == 0):
			self.white_groups.join(self.EDGE1, cell)
		if(cell[0] == self.size -1):
			self.white_groups.join(self.EDGE2, cell)
		#join any groups connected by the new white stone
		for n in self.neighbors(cell):
			if(self.board[n] == self.PLAYERS["white"]):
				self.white_groups.join(n, cell)

	def place_black(self, cell):
		"""
		Place a black stone regardless of whose turn it is.
		"""
		if(self.board[cell] == self.PLAYERS["none"]):
			self.board[cell] = self.PLAYERS["black"]
			self.empty.remove(cell)
		else:
			raise ValueError("Cell occupied")
		#if the placed cell touches a black edge connect it appropriately
		if(cell[1] == 0):
			self.black_groups.join(self.EDGE1, cell)
		if(cell[1] == self.size -1):
			self.black_groups.join(self.EDGE2, cell)
		#join any groups connected by the new black stone
		for n in self.neighbors(cell):
			if(self.board[n] == self.PLAYERS["black"]):
				self.black_groups.join(n, cell)

	def turn(self):
		"""
		Return the player with the next move.
		"""
		return self.toplay

	def set_turn(self, player):
		"""
		Set the player to take the next move.
		"""
		if(player in self.PLAYERS.values() and player !=self.PLAYERS["none"]):
			self.toplay = player
		else:
			raise ValueError('Invalid turn: ' + str(player))

	def winner(self):
		"""
		Return a number corresponding to the winning player,
		or none if the game is not over.
		"""
		if(self.white_groups.connected(self.EDGE1, self.EDGE2)):
			return self.PLAYERS["black"]
		elif(self.black_groups.connected(self.EDGE1, self.EDGE2)):
			return self.PLAYERS["white"]
		else:
			return self.PLAYERS["none"]
		
	def would_lose(self, cell, color):
		"""
		Return True is the move indicated by cell and color would lose the game,
		False otherwise.
		"""
		connect1 = False
		connect2 = False
		if color == self.PLAYERS["black"]:
			if cell[1] == 0:
				connect1 = True
			elif cell[1] == self.size - 1:
				connect2 = True
			for n in self.neighbors(cell):
				if self.black_groups.connected(self.EDGE1, n):
					connect1 = True
				elif self.black_groups.connected(self.EDGE2, n):
					connect2 = True
		elif color == self.PLAYERS["white"]:
			if cell[0] == 0:
				connect1 = True
			elif cell[0] == self.size - 1:
				connect2 = True
			for n in self.neighbors(cell):
				if self.white_groups.connected(self.EDGE1, n):
					connect1 = True
				elif self.white_groups.connected(self.EDGE2, n):
					connect2 = True
			
		return connect1 and connect2
	
	def show_board(self, player):
		ret = '\n'
		coord_size = len(str(self.size))
		offset = 1
		ret+=' '*(offset+1)
		for x in range(self.size):
			ret+=chr(ord('A')+x)+' '*offset*2
		ret+='\n'
		for y in range(self.size):
			ret+=str(y+1)+' '*(offset*2+coord_size-len(str(y+1)))
			for x in range(self.size):
				if(self.board[x, y] == self.PLAYERS["white"] and
			           (self.revealed[x, y] == self.DARK_STATE["visible"] or
			           player == self.PLAYERS["white"])):
					ret+=self.DISP_WHITE
				elif(self.board[x,y] == self.PLAYERS["black"] and
			             (self.revealed[x, y] == self.DARK_STATE["visible"] or
			             player == self.PLAYERS["black"])):
					ret+=self.DISP_BLACK
				else:
					ret+=self.DISP_EMPTY
				ret+=' '*offset*2
			ret+=self.DISP_WHITE+"\n"+' '*offset*(y+1)
		ret+=' '*(offset*2+1)+(self.DISP_BLACK+' '*offset*2)*self.size

		return ret			

	def neighbors(self, cell, color=None):
		"""
		Return list of neighbors of the passed cell.
		"""
		if cell == self.EDGE1:
			if color == self.PLAYERS["black"]:
				nb = []
				for i in range(self.size):
					nb.append((i, 0))
			elif color == self.PLAYERS["white"]:
				nb = []
				for i in range(self.size):
					nb.append((0, i))
			return nb
		elif cell == self.EDGE2:
			nb = []
			if color == self.PLAYERS["black"]:
				for i in range(self.size):
					nb.append((i, self.size -1))
			elif color == self.PLAYERS["white"]:
				for i in range(self.size):
					nb.append((self.size -1, i))
			return nb
		x = cell[0]
		y=cell[1]
		return [(n[0]+x , n[1]+y) for n in self.neighbor_patterns\
			if (0<=n[0]+x and n[0]+x<self.size and 0<=n[1]+y and n[1]+y<self.size)]

	def moves(self):
		"""
		Get a list of all moves possible on the current board.
		"""
		moves = []
		for y in range(self.size):
			for x in range(self.size):
				if self.board[x,y] == self.PLAYERS["none"]:
					moves.append((x,y))
		return moves
	
	def blank_ldiagonal(self):
		"""
		Returns True if all the cells on the long diagonal of the board are blank. False otherwise.
		"""
		for i in range(self.size):
			if self.board[i, i] != self.PLAYERS["none"]:
				return False
		return True
		
	def blank_sdiagonal(self):
		"""
		Returns True if all the cells on the short diagonal of the board are blank. False otherwise.
		"""
		for i in range(self.size):
			if self.board[i, self.size - i - 1] != self.PLAYERS["none"]:
				return False
		return True
	
	def get_color(self, cell):
		return self.board[cell[0], cell[1]]
	
	def reachable(self, colors, stopset, start):
		"""
		Returns a set containing the cells reachable from start by going through cells of a color in colors
		and without crossing cells in the stopset.
		"""
		seen = set([start])
		queue = deque([start])
		while len(queue) > 0:
			cell = queue.popleft()
			if cell in stopset:
				continue
			
			for nb in self.neighbors(cell, colors[0]):
				if self.get_color(nb) in colors and nb not in seen:
					queue.append(nb)
					seen.add(nb)
					
		return seen
	
	def get_empty_cell_set(self):
		return self.empty
	
	def connected(self, color, cell1, cell2):
		if color == self.PLAYERS["black"]:
			return self.black_groups.connected(cell1, cell2)
		elif color == self.PLAYERS["white"]:
			return self.white_groups.connected(cell1, cell2)

	def __str__(self):
		"""
		Print an ascii representation of the game board.
		"""
		ret = '\n'
		coord_size = len(str(self.size))
		offset = 1
		ret+=' '*(offset+1)
		for x in range(self.size):
			ret+=chr(ord('A')+x)+' '*offset*2
		ret+='\n'
		for y in range(self.size):
			ret+=str(y+1)+' '*(offset*2+coord_size-len(str(y+1)))
			for x in range(self.size):
				if(self.board[x, y] == self.PLAYERS["white"]):
					ret+=self.DISP_WHITE
				elif(self.board[x,y] == self.PLAYERS["black"]):
					ret+=self.DISP_BLACK
				else:
					ret+=self.DISP_EMPTY
				ret+=' '*offset*2
			ret+=self.DISP_WHITE+"\n"+' '*offset*(y+1)
		ret+=' '*(offset*2+1)+(self.DISP_BLACK+' '*offset*2)*self.size

		return ret
	
	
