# A test that a the dead cell analysis player correctly detects dead cells.


from gtpinterface2 import gtpinterface2

basic = gtpinterface2("basic")
improved = gtpinterface2("dca")
black = basic
white = improved
score1 = 0
score2 = 0

basic.gtp_boardsize(["7"])
basic.gtp_time("1")
improved.gtp_boardsize(["7"])
improved.gtp_time("1")

improved.gtp_play(["b", "d2"])
improved.gtp_play(["b", "c2"])
improved.gtp_play(["b", "b3"])
improved.gtp_play(["b", "b4"])
improved.gtp_play(["b", "c4"])
improved.gtp_play(["b", "d3"])
print(improved.gtp_genmove("")[1])
print(improved.gtp_show("")[1])

