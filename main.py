from StateMachine import *
address = ("localhost", 8000)
period = 1
sm = StateMachine(period, address)

#sm.start()
sm.run()