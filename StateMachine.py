import threading
import time
import pysimpledmx
import numpy as np
import random

ROWS = 5
COLS = 6

IDLE = "IDLE"
ANOTHER_STATE = "ANOTHER_STATE"

class StateMachine(threading.Thread):
	"""docstring for StateMachine"""

	def __init__(self, period, address):
		super(StateMachine, self).__init__()
		self.cur_state = IDLE
		self.period = period

		self.time = time.time()
		self.next_execute_time = self.time + self.period

		self.dmx = pysimpledmx.DMXConnectionEthernet(address)

		grid = []
		for i in xrange(ROWS):
			row = [(0,0,0)]*COLS
			grid.append(row)
		self.grid = np.array(grid)
		print self.grid

	def run(self):
		while True:
			if self.time > self.next_execute_time:
				self.execute()
				self.next_execute_time += self.period
			else:
				time.sleep(0.001)
			self.time = time.time()

	def execute(self):
		next_state = self.cur_state

		if self.cur_state == IDLE:
			self.idle()
			next_state = ANOTHER_STATE
		elif self.cur_state == ANOTHER_STATE:
			self.another_state()

		if(next_state != self.cur_state):
			print "%s -> %s"%(self.cur_state, next_state)
			self.cur_state = next_state

		self.renderDMX()
		print "Executing"

	def idle(self):
		pass

	def another_state(self):
		#print self.grid
                pass

	def renderDMX(self):
		for r in xrange(ROWS):
			for c in xrange(COLS):
				val = self.grid[r, c]
				for i in xrange(3):
					chan = r*COLS*3 + c*3 + i + 1
					#print chan
					self.dmx.setChannel(chan, random.randint(1,255))
		self.dmx.render()
		
