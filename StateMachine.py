import threading
import time
import pysimpledmx
import numpy as np
from scipy import signal
import random
from Tkinter import *


ROWS = 5
COLS = 6
WIDTH = COLS*20
HEIGHT = ROWS*20

OFF_STATE = "OFF_STATE"
FADE_STATE = "FADE_STATE"
IDLE_STATE = "IDLE_STATE"
PULSE_STATE = "PULSE_STATE"

def random_grid():
	grid = []
	for i in xrange(ROWS):
		row = []
		for j in xrange(COLS):
			row.append((random.randint(0,255),random.randint(0,255),random.randint(0,255)))
		grid.append(row)
	return np.array(grid)

class StateMachine(threading.Thread):
	"""docstring for StateMachine"""

	def __init__(self, period, address, show_gui=False):
		super(StateMachine, self).__init__()
		self.cur_state = OFF_STATE
		self.state_time = 0
		self.period = period

		self.time = time.time()
		self.next_execute_time = self.time + self.period

		self.dmx = pysimpledmx.DMXConnectionEthernet(address)

		# 2D Array of Color (r,g,b) tuples
		grid = []
		for i in xrange(ROWS):
			row = [(0,0,0)]*COLS
			grid.append(row)
		self.grid = np.array(grid)

		self.show_gui = show_gui
		if show_gui:
			self.gui_thread = threading.Thread(target = self.run_gui)
			self.gui_thread.start()

	def run_gui(self):
		self.root = Tk()
		self.canvas = Canvas(self.root, width=WIDTH, height=HEIGHT)
		self.canvas.pack()
		self.root.after(50, self.draw)
		self.root.mainloop()

	def run(self):
		"""
		Starts the time triggered state machine.
		"""
		while True:
			if self.time > self.next_execute_time:
				self.execute()
				self.next_execute_time += self.period
			else:
				time.sleep(0.001)
			self.time = time.time()

	def draw(self):
		for r in xrange(ROWS):
			for c in xrange(COLS):
				w = WIDTH/COLS
				h = HEIGHT/ROWS
				red = self.grid[r,c,0]
				green = self.grid[r,c,1]
				blue = self.grid[r,c,2]
				color = "#%02x%02x%02x" % (red, green, blue)
				self.canvas.create_rectangle(r*w, c*h, (r+1)*w, (c+1)*h, fill=color)
		self.root.after(50, self.draw)

	def execute(self):
		"""
		Executes the current state and calculates the next state.
		"""
		next_state = self.cur_state
		self.state_time += self.period

		if self.cur_state == OFF_STATE:
			self.off_state()

			# Set of params for fading
			self.set_fade(np.array(self.grid), random_grid(), 5.0)
			next_state = FADE_STATE

		elif self.cur_state == IDLE_STATE:
			self.idle_state()
			# Probably a lot of trnasitions here
			next_state = IDLE_STATE

		elif self.cur_state == FADE_STATE:
			# self.fade_time
			# self.start_grid
			# self.end_grid
			self.fade_state()
			if self.state_time >= self.fade_time:
				self.set_pulse(1.0, bounce=False)
				next_state = PULSE_STATE

		elif self.cur_state == PULSE_STATE:
			self.pulse_state()

		# Render the new lights
		self.render_leds()

		# Print transitions
		if(next_state != self.cur_state):
			self.state_time = 0
			print "%s -> %s"%(self.cur_state, next_state)
			self.cur_state = next_state

	#######################
	### State Functions ###
	#######################
	def off_state(self):
		self.grid = self.grid * 0

	def idle_state(self):
		pass

	def fade_state(self):
		time = min(self.state_time, self.fade_time)
		a = float(time)/self.fade_time
		b = 1 - a

		self.grid = a*self.end_grid + b*self.start_grid
		self.grid = self.grid.astype(int)

	def pulse_state(self):
		if self.pulse_bounce:
			self.grid = self.end_grid * (0.5*np.sin(2*np.pi*self.pulse_freq*self.state_time) + 0.5)
		else:
			self.grid = self.end_grid * (0.5*signal.sawtooth(2*np.pi*self.pulse_freq*self.state_time) + 0.5)

		self.grid = np.clip(self.grid, 0, 255)
		self.grid = self.grid.astype(int)

	########################
	### Helper Functions ###
	########################

	def set_fade(self, start_grid, end_grid, fade_time):
		self.start_grid = start_grid
		self.fade_time = fade_time
		self.end_grid = end_grid

	def set_pulse(self, freq, bounce=False, end_grid=None):
		self.pulse_freq = freq
		self.pulse_bounce = bounce
		if end_grid:
			self.end_grid = end_grid
		else:
			self.end_grid = np.array(self.grid)

	def render_leds(self):
		"""
		Send the self.grid values to the DMX Controller to render the LED lights
		"""
		for r in xrange(ROWS):
			for c in xrange(COLS):
				val = self.grid[r, c]
				for i in xrange(3):
					chan = r*COLS*3 + c*3 + i + 1
					self.dmx.setChannel(chan, val[i])
		self.dmx.render()
		
