"""
Monte Carlo tree search reverse hex player with poolRAVE
by Isabel McCarten
starter code from Mopyhex at https://github.com/yotomyoto/mopyhex
"""
from mctsagent import *

class rave_node(node):
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
		self.outcome = gamestate.PLAYERS["none"]

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

class poolrave_mctsagent(mctsagent):
	RAVE_CONSTANT = 300
	
	CASE2 = {(0, 1): (1, 1), (1, 1): (0, 1)}
	CASE2 = {(0, 1): (1, 1), (1, 1): (0, 1)}
	CASE2_FIRST = [(0, 0)]
	CASE2_SINGLE = (1, 0)
	
	CASE3 = {(0, 1): (0, 2), (0, 2): (0, 1), (2, 0): (2, 1), (2, 1): (2, 0)}
	CASE3_FIRST = [(0, 0), (1, 0), (1, 2), (2, 2)]
	CASE3_SINGLE = (1, 1)
	
	CASE4 = {(2, 0): (3, 0), (3, 0): (2, 0), (2, 2): (3, 1), (3, 1): (2, 2), (1, 2): (3, 2),
                 (3, 2): (1, 2), (0, 3): (1,3), (1, 3): (0, 3), (2, 3): (3, 3), (3, 3): (2, 3)}
	CASE4_FIRST = [(0, 0), (1, 0), (0, 1), (0, 2), (1, 1)]
	CASE4_SINGLE = (2, 1)
	
	CASE5 = {(0, 1): (0, 2), (0, 2): (0, 1), (0, 3): (0, 4), (0, 4): (0, 3), (1, 1): (1, 3), (1, 3): (1, 1),
                 (1, 2): (2, 1), (2, 1): (1, 2), (3, 1): (3, 3), (3, 3): (3, 1), (2, 3): (3, 2), (3, 2): (2, 3),
                 (4, 0): (4, 1), (4, 1): (4, 0), (4, 2): (4, 3), (4, 3): (4, 2)}
	CASE5_FIRST = [(0, 0), (1, 0), (2, 0), (3, 0), (1, 4), (2, 4), (3, 4), (4, 4)]
	CASE5_SINGLE = (2, 2)
	
	def __init__(self, state=gamestate(8)):
		super().__init__(state)
		self.black_rave = {}
		self.white_rave = {}
		self.short_symetrical = True		
	
	def special_case(self, last_move):
		size = self.rootstate.size
		moves = self.rootstate.moves()
		if size == 2 and self.rootstate.turn() == gamestate.PLAYERS["white"]:
			if last_move in self.CASE2 and self.CASE2[last_move] in moves:
				return self.CASE2[last_move]
			elif last_move in self.CASE2 and self.CASE2[last_move] not in moves or last_move == self.CASE2_SINGLE:
				for key in self.CASE2.keys():
					if key in moves and self.CASE2[key] in moves:
						return key
			for cell in self.CASE2_FIRST:
				if cell in moves:
					return cell
		elif size == 3 and self.rootstate.turn() == gamestate.PLAYERS["black"]:
			if last_move in self.CASE3 and self.CASE3[last_move] in moves:
				return self.CASE3[last_move]
			elif last_move in self.CASE3 and self.CASE3[last_move] not in moves or last_move == self.CASE3_SINGLE:
				for key in self.CASE3.keys():
					if key in moves and self.CASE3[key] in moves:
						return key
			for cell in self.CASE3_FIRST:
				if cell in moves:
					return cell
		elif size == 4 and self.rootstate.turn() == gamestate.PLAYERS["white"]:
			if last_move in self.CASE4 and self.CASE4[last_move] in moves:
				return self.CASE4[last_move]	
			elif last_move in self.CASE4 and self.CASE4[last_move] not in moves or last_move == self.CASE4_SINGLE:
				for key in self.CASE4.keys():
					if key in moves and self.CASE4[key] in moves:
						return key			
			for cell in self.CASE4_FIRST:
				if cell in moves:
					return cell
			
		elif size == 5 and self.rootstate.turn() == gamestate.PLAYERS["black"]:
			if last_move in self.CASE5 and self.CASE5[last_move] in moves:
				return self.CASE5[last_move]			
			elif last_move in self.CASE5 and self.CASE5[last_move] not in moves or last_move == self.CASE5_SINGLE:
				for key in self.CASE5.keys():
					if key in moves and self.CASE5[key] in moves:
						return key			
			for cell in self.CASE5_FIRST:
				if cell in moves:
					return cell	
			
		elif self.rootstate.num_played == 0 and size % 2 == 0:
			return random.choice([(0, 0), (size - 1, size - 1)])
		elif self.rootstate.num_played == 1 and size % 2 == 1:
			if last_move[0] != last_move[1]:  # if the first move was not on the long diagonal
				return (last_move[1], last_move[0])
			elif last_move[0] == (size - 1) / 2 and last_move[1] == (size - 1) / 2:
				return random.choice((0, 0), (size - 1, size - 1))
			else:
				return (size - 1 - last_move[0], size - 1 - last_move[1])
		elif size % 2 == 1 and self.rootstate.num_played % 2 == 1:
			if self.rootstate.blank_ldiagonal():
				self.short_symetrical = False
				return (last_move[1], last_move[0])
			
			elif self.rootstate.blank_sdiagonal() and self.short_symetrical:
				return (size - 1 - last_move[0], size - 1 - last_move[1])
			
		return None

	def best_move(self):
		"""
		Return the best move according to the current tree.
		"""
		if(self.rootstate.winner() != gamestate.PLAYERS["none"]):
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
		self.root = rave_node()


	def search(self, time_budget):
		"""
		Search and update the search tree for a specified amount of time in secounds.
		"""
		startTime = time.clock()
		num_rollouts = 0

		#do until we exceed our time budget
		while(time.clock() - startTime <time_budget):
			node, state = self.select_node()
			turn = state.turn()
			outcome, black_rave_pts, white_rave_pts = self.roll_out(state)
			self.backup(node, turn, outcome, black_rave_pts, white_rave_pts)
			num_rollouts += 1

		#stderr.write("Ran "+str(num_rollouts)+ " rollouts in " +\
		#	str(time.clock() - startTime)+" sec\n")
		#stderr.write("Node count: "+str(self.tree_size())+"\n")

	def select_node(self):
		"""
		Select a node in the tree to preform a single simulation from.
		"""
		node = self.root
		state = deepcopy(self.rootstate)

		#stop if we reach a leaf node
		while(len(node.children)!=0):
			max_value = max(node.children.values(), key = lambda n: n.value(self.EXPLORATION, self.RAVE_CONSTANT)).value(self.EXPLORATION, self.RAVE_CONSTANT)
			#decend to the maximum value node, break ties at random
			max_nodes = [n for n in node.children.values() if n.value(self.EXPLORATION, self.RAVE_CONSTANT) == max_value]
			node = random.choice(max_nodes)
			state.play(node.move)

			#if some child node has not been explored select it before expanding
			#other children
			if node.N == 0:
				return (node, state)

		#if we reach a leaf node generate its children and return one of them
		#if the node is terminal, just return the terminal node
		if(self.expand(node, state)):
			node = random.choice(list(node.children.values()))
			state.play(node.move)
		return (node, state)


	def backup(self, node, turn, outcome, black_rave_pts, white_rave_pts):
		"""
		Update the node statistics on the path from the passed node to root to reflect
		the outcome of a randomly simulated playout.
		"""
		#note that reward is calculated for player who just played
		#at the node and not the next player to play
		reward = -1 if outcome == turn else 1

		while node!=None:
			if turn == gamestate.PLAYERS["white"]:
				for point in white_rave_pts:
					if point in node.children:
						node.children[point].Q_RAVE+=-reward
						node.children[point].N_RAVE+=1
			else:
				for point in black_rave_pts:
					if point in node.children:
						node.children[point].Q_RAVE+=-reward
						node.children[point].N_RAVE+=1

			node.N += 1
			node.Q +=reward
			if turn == gamestate.PLAYERS["black"]:
				turn = gamestate.PLAYERS["white"]
			else:
				turn = gamestate.PLAYERS["black"]
			reward = -reward
			node = node.parent

	def expand(self, parent, state):
		"""
		Generate the children of the passed "parent" node based on the available
		moves in the passed gamestate and add them to the tree.
		"""
		children = []
		if(state.winner() != gamestate.PLAYERS["none"]):
		#game is over at this node so nothing to expand
			return False


		for move in state.moves():
			children.append(rave_node(move, parent))

		parent.add_children(children)
		return True

	def set_gamestate(self, state):
		"""
		Set the rootstate of the tree to the passed gamestate, this clears all
		the information stored in the tree since none of it applies to the new 
		state.
		"""
		self.rootstate = deepcopy(state)
		self.root = rave_node()
		self.white_reply = {}
		self.black_reply = {}

	def roll_out(self, state):
		"""Simulate a random game except that we play all known critical
		cells first, return the winning player and record critical cells at the end."""
		moves = state.moves()
		black_rave_moves = sorted(self.black_rave.keys(), key=lambda cell: self.black_rave[cell])
		white_rave_moves = sorted(self.white_rave.keys(), key=lambda cell: self.white_rave[cell])
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
		while(state.winner() == gamestate.PLAYERS["none"]):
			move = None
			if len(black_pool) > 0 and state.turn() == gamestate.PLAYERS["black"]:
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
				if state.board[(x,y)] == gamestate.PLAYERS["black"]:
					black_rave_pts.append((x,y))
					if state.winner() == gamestate.PLAYERS["black"]:
						if (x, y) in self.black_rave:
							self.black_rave[(x, y)] += 1
						else:
							self.black_rave[(x, y)] = 1
					else:
						if (x, y) in self.black_rave:
							self.black_rave[(x, y)] -= 1
						else:
							self.black_rave[(x, y)] = -1
				elif state.board[(x,y)] == gamestate.PLAYERS["white"]:
					white_rave_pts.append((x,y))
					if state.winner() == gamestate.PLAYERS["white"]:
						if (x, y) in self.white_rave:
							self.white_rave[(x, y)] += 1
						else:
							self.white_rave[(x, y)] = 1
					else:
						if (x, y) in self.white_rave:
							self.white_rave[(x, y)] -= 1
						else:
							self.white_rave[(x, y)] = -1

		#print (num_pool)
		return state.winner(), black_rave_pts, white_rave_pts		

	def tree_size(self):
		"""
		Count nodes in tree by BFS.
		"""
		Q = Queue()
		count = 0
		Q.put(self.root)
		while not Q.empty():
			node = Q.get()
			count +=1
			for child in node.children.values():
				Q.put(child)
		return count

