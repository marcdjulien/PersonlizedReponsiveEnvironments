import threading
import socket
import struct
from oscinput import OSCInput

class KinectInput(threading.Thread):
    def __init__(self, address):
        super(KinectInput, self).__init__()
        self.address = address
        self.done = False
        self.data = []
        self.osc = OSCInput(address)
        self.n = 0
        self.grid_locs = []
        
    def run(self):
        self.osc.start()
        print "KinectInput: Starting Server"
        while not self.done:
            data, addr = self.sock.recvfrom(1024)
            data = struct.unpack("b"*len(data), data)
            string = "".join(map(chr, data))
            if "new_user" in string:
                self.add_user(string)
            elif "lost_user" in string:
                self.remove_user(string)
            else: #user ID x y z q
                self.update_locations(string)
            if self.n < 0:
                self.n = 0
            print string
            print "# Users: " + str(self.n)
            print "Locations: "+ str(self.grid_locs)
        self.osc.close()
        print "KinectInput: Thread finished."

    def add_user(self, string):
        pass
    def remove_user(self, string):
        pass
    def update_locations(self, string):
        pass

        
    def close(self):
        self.done = True
