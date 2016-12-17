# RHex

Reverse hex is a game played on a diamond shaped board of hexagonal cells where two players alternate placing white and black stones on the cells. 
Similar to the game hex, two non-adjacent sides of the board are assigned to the black player, and the other two sides are assigned to the white player,
but the winning condition is the opposite of hex’s. The first player to connect their sides loses. It is explained in more detail in [3].

RHex is a simple implementation of reverse hex with a set of players.
It includes a basic Monte Carlo tree search based player with Rapid Action Value Estimation (RAVE) modified from mopyhex [2]
and four variations exploring possible improvements to the player. All of the players other than the basic on use an opening book and a 
static guaranteed winning strategy for boards smaller 6 x 6 for the player with the turn order advantage.
The player files are:
- rave_mctsagent.py: the basic MCTS with RAVE player
- dca_mctsagent.py: the one using dead cell analysis [4]. The implementation also borrows some ideas from benzene [7].
- poolrave_mctsagent.py: the one using the poolRAVE variation of Monte Carlo tree search [5]
- lgr_mctsagent.py: the one using the Last Good Reply algorithm [6] 
- decisive_move_mctsagent.py: the one using Decisive Moves [1] in the tree search rollout policy

[1]	C Browne, E Powley, D Whitehouse, S Lucas, P I Cowling, P Rohlfshagen, S Tavener, D Perez, S Samothrakis, and S Colton. A survey of monte carlo tree search methods. In IEEE Transactions on Computational Intelligence and AI in Games, vol.4, no.1, pages 1-43, 2012.
[2]	Kenny Young. Mopyhex. https://github.com/yotomyoto/mopyhex, 2015. Accessed 2016-02-19.
[3]	R Hayward, B Toft, and P Henderson. How to play reverse hex. In Discrete Mathematics, vol. 312, no. 1, pages 148-156, 2012.
[4]	R Hayward. A puzzling hex primer. In Michael H. Albert and Richard J. Nowakowski,
editors, Games of No Chance 3, pages 151-162. Cambridge University Press, 2009.
[5]	J Hoock, C Lee, A Rimmel, F Teytaud, O Teytaud, and M Wang. Intelligent agents for the game of go. In IEEE Comput. Intell. Mag., vol. 5, no. 4, pages 28–42, 2010.
[6]	P Drake. The last-good-reply policy for monte-carlo go. In Int. Comp. Games Assoc. J., vol. 32, no. 4, pages 221–227, 2009.
[7]	J Pawlewicz. Benzene. https://github.com/jakubpawlewicz/benzene, 2012. Accessed 2016-04-12.
