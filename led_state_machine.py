import random
import threading
import time
import socket
from Tkinter import *
from scipy import signal
import pysimpledmx
from Constants import *

ROWS = 5
COLS = 6
WIDTH = COLS*20
HEIGHT = ROWS*20

OFF_STATE = "OFF_STATE"
FADE_STATE = "FADE_STATE"
IDLE_STATE = "IDLE_STATE"
PULSE_STATE = "PULSE_STATE"
SPOT_LIGHT_STATE = "SPOT_LIGHT_STATE"
EXIT_STATE = "EXIT_STATE"
NEW_POLL_BYTE = 100

#POLL_TIME = [2*60, 4*60, 6*60, 8*60, 10*60]
POLL_TIME = [30, 60, 90, 120, 150]


def random_grid():
    grid = []
    for i in xrange(ROWS):
        row = []
        for j in xrange(COLS):
            row.append(random_color())
        grid.append(row)
    return np.array(grid)


def random_color():
    return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)

def n_adjusted_array(old_grid, n):
        brightness = {1: 0.1,
                      2: 0.3,
                      3: 0.6,
                      4: 1.0}
        new_grid = []
        n += 1
        n = min(n ,4)
        b = brightness[n]
        for r in xrange(ROWS):
                row = []
                for c in xrange(COLS):
                    color = [0, 0, 0]
                    for v in xrange(3):
                            color[v] = old_grid[r][c][v]*ADJUST_ARRAY[r][c]*b
                    row.append(color)
                new_grid.append(row)
        return new_grid

class LEDStateMachine(threading.Thread):
    """docstring for StateMachine"""
    def __init__(self, period, led_dmx_address, light_dmx_address, max_output_address, osc, kinect, show_gui=False):
        super(LEDStateMachine, self).__init__()
        self.cur_state = OFF_STATE
        self.state_time = 0
        self.period = period

        self.time = time.time()
        self.next_execute_time = self.time + self.period

        self.leddmx = pysimpledmx.DMXConnectionEthernet(led_dmx_address, universe=0)
        self.lightdmx = pysimpledmx.DMXConnectionEthernet(light_dmx_address, universe=1)
        self.max_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.max_output_address = max_output_address

        self.osc = osc
        self.kinect = kinect
        self.old_n = 0
        self.poll_index = 0

        # 2D Array of Color (r,g,b) tuples
        grid = []
        for i in xrange(ROWS):
            row = [(0,0,0)]*COLS
            grid.append(row)
        self.grid = np.array(grid)
        # What the lights should be
        self.lights = np.array([0, 0, 0, 0])
        # What the lights are
        self.vlights = np.array([0, 0, 0, 0])

        self.show_gui = show_gui
        if show_gui:
            self.gui_thread = threading.Thread(target = self.run_gui)
            self.gui_thread.start()

    def run_gui(self):
        self.root = Tk()
        self.canvas = Canvas(self.root, width=WIDTH, height=HEIGHT)
        self.canvas.pack()
        self.root.after(int(self.period*1000), self.draw)
        self.root.mainloop()

    def run(self):
        """
        Starts the time triggered state machine.
        """
        print "LEDStateMachine: Running LEDStateMachine"
        self.done = False
        while not self.done:
            if self.time > self.next_execute_time:
                self.execute()
                self.next_execute_time += self.period
            else:
                time.sleep(0.001)
            self.time = time.time()
        self.root.destroy()
        print "LEDStateMachine: Thread finished."

    def draw(self):
        for r in xrange(ROWS):
            for c in xrange(COLS):
                w = WIDTH/COLS
                h = HEIGHT/ROWS
                red = self.grid[r,c,0]
                green = self.grid[r,c,1]
                blue = self.grid[r,c,2]
                color = "#%02x%02x%02x" % (red, green, blue)
                self.canvas.create_rectangle(c*w, r*h, (c+1)*w, (r+1)*h, fill=color)
        self.root.after(50, self.draw)

    def execute(self):
        """
        Executes the current state and calculates the next state.
        """
        next_state = self.cur_state
        self.state_time += self.period

        #Always transition the lights
        self.vlights = self.vlights*0.5 + self.lights*0.5

        if self.cur_state == OFF_STATE:
            self.off_state()
            self.start_time = time.time()
            self.poll_index = 0
            if self.state_time > 3.0:
                next_state = IDLE_STATE

        elif self.cur_state == IDLE_STATE:
            self.idle_state()
            self.time = time.time() - self.start_time
            # Keeps track of the number of people in the room
            # and adjust the brightness
            if self.old_n != self.kinect.n:
                # Tell MAX
                self.send_max(self.kinect.n)

                # set fade for leds
                old_arr = np.array(self.grid)
                new_arr = np.array(n_adjusted_array(NEUTRAL_LEDS, self.kinect.n))
                fade_time = 2.5
                self.set_fade(old_arr, new_arr, fade_time)

                #set stage lights
                self.lights = np.array([25,25,25,25])*self.kinect.n

                # Update n variable
                self.old_n = self.kinect.n

                next_state = FADE_STATE

            # It is time for the new poll results
            # Pulse the lights for a breif amount of time
            elif self.time > POLL_TIME[self.poll_index]:
                # Tell MAX
                self.send_max(NEW_POLL_BYTE)
                freq = 1.0
                bounce = False
                self.set_pulse(freq, bounce)
                self.poll_index += 1
                if self.poll_index > 4:
                    self.poll_index = 4
                next_state = PULSE_STATE
            elif self.osc.get_val("/2/push4") == 1:
                next_state = EXIT_STATE

        elif self.cur_state == FADE_STATE:
            self.fade_state()
            if self.state_time >= self.fade_time:
                next_state = IDLE_STATE

        elif self.cur_state == PULSE_STATE:
            self.pulse_state()
            if self.state_time > 5.0:
                self.grid = self.end_grid
                next_state = IDLE_STATE

        elif self.cur_state == SPOT_LIGHT_STATE:
            self.spot_light_state()
            if self.state_time > self.spot_light_time:
                next_state = IDLE_STATE
        elif self.cur_state == EXIT_STATE:
            self.exit()

        # Render the new lights
        self.render_lighting()

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
        self.lights = 0*self.lights

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
            self.grid = self.end_grid * (0.25*np.sin(2*np.pi*self.pulse_freq*self.state_time) + 0.75)
        else:
            self.grid = self.end_grid * (0.25*signal.sawtooth(2*np.pi*self.pulse_freq*self.state_time) + 0.75)

        self.grid = np.clip(self.grid, 0, 255)
        self.grid = self.grid.astype(int)

    def spot_light_state(self):
        self.grid *= 0
        self.grid[self.spot_light_row, self.spot_light_col, :] = self.spot_light_color

    ########################
    ### Helper Functions ###
    ########################
    def send_max(self, info_byte):
        print "Sending to MAX:"+str(info_byte);
        self.max_socket.sendto(chr(info_byte),self.max_output_address)

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

    def set_spot_light(self, row, col, color, time):
        self.spot_light_row = row
        self.spot_light_col = col
        self.spot_light_color = color
        self.spot_light_time = time

    def render_lighting(self):
        """
        Send the self.grid values to the DMX Controller to render the LED lights
        Send the self.vlight values to the DMX Controller to render the Stage Lights
        """
        chan = 0
        for r in xrange(ROWS):
            for c in xrange(COLS):
                val = self.grid[r, c]
                for i in xrange(4):
                    if i == 3:
                        self.leddmx.setChannel(chan, 0)
                    else:
                        self.leddmx.setChannel(chan, val[i])
                chan +=1

        for i in xrange(4):
            self.lightdmx.setChannel(200+i, int(self.vlights[i]))

        self.lightdmx.render()
        self.leddmx.render()

    def exit(self):
        self.done = True
