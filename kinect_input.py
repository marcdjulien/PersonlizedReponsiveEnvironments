import threading
import socket
import struct
class KinectInput(threading.Thread):
    def __init__(self, address):
        super(KinectInput, self).__init__()
        self.address = address
        self.done = False
        self.data = []
        self.n = 0
        
    def run(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(self.address)
        print "KinectInput: Starting Server"
        while not self.done:
            data, addr = self.sock.recvfrom(1024)
            data = struct.unpack("b"*len(data), data)
            string = "".join(map(chr, data))
            if "new_user" in string:
                self.n += 1
            elif "lost_user" in string:
                self.n -= 1
            if self.n < 0:
                self.n = 0
            print string
            print "# Users: " + str(self.n)
        print "KinectInput: Thread finished."
        
    def close(self):
        self.done = True
