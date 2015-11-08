from StateMachine import *
ART_NET_UDP_PORT = 6454
dmx_address = ("10.7.158.185", ART_NET_UDP_PORT)

period = 0.050 # In seconds
sm = StateMachine(period, dmx_address, show_gui=True)
#sm.start()
sm.run()
