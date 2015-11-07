from StateMachine import *
ART_NET_UDP_PORT = 6454
address = ("localhost", 8000)
dmx = ("10.7.158.185", ART_NET_UDP_PORT)
period = 1
sm = StateMachine(period, dmx)

#sm.start()
sm.run()
