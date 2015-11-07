from StateMachine import *
ART_NET_UDP_PORT = 6454
dmx_address = ("10.7.158.185", ART_NET_UDP_PORT)

period = 1 # In seconds
sm = StateMachine(period, dmx_address)
#sm.start()
sm.run()
