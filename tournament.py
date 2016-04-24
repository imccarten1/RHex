"""
code for testing different reverse hex players against each other
by Isabel McCarten
"""

from gtpinterface2 import gtpinterface2

basic = gtpinterface2("basic")
improved = gtpinterface2("dca")
black = basic
white = improved
score1 = 0
score2 = 0

basic.gtp_boardsize("7")
basic.gtp_time("1")
improved.gtp_boardsize("7")
improved.gtp_time("1")

for i in range(20):
    black.gtp_clear("")
    white.gtp_clear("")
    
    while black.gtp_winner("")[1] == "none":
        move = white.gtp_genmove("")[1]
        #print("white")
        #print(move)
        black.gtp_play(["white ", move])
        #print(black.gtp_show("")[1])
        if black.gtp_winner("")[1] == "none":
            move = black.gtp_genmove("")[1]
            #print("black")
            #print(move)
            white.gtp_play(["b ", move])
            #print(black.gtp_show("")[1])
            
    if improved == black and black.gtp_winner("")[1] == "black":
        score1 += 1
    elif improved == white and white.gtp_winner("")[1] == "white":
        score2 += 1
        
    print ("score")
    print(black.gtp_winner("")[1])
    print (score1)
    print (score2)
    print (i)
    print (black.gtp_show("")[1])
    black, white = white, black