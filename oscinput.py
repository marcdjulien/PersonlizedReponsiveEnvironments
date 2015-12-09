from OSC import OSCServer
import threading
import time


class OSCInput(threading.Thread):
    """docstring for OSCInput"""
    def __init__(self, address):
        super(OSCInput, self).__init__()
        self.address = address
        self.server = OSCServer(address)
        self.server.addMsgHandler( "default", self.default_callback )
        self.values = {}        

    def default_callback(self, path, tags, args, source):
        print time.time(), path, args
        if(len(args) == 1):
            self.values[path] = args[0]
        else:
            self.values[path] = args

    def get_val(self, name):
        if name in self.values.keys():
            return self.values[name]
        else:
            return None
    
    def run(self):
        print "OSCInput: Running OSCInput"
        self.server.serve_forever()
        print "OSCInput: Thread finished"

    def close(self):
        self.server.close()


class KinectOSCInput(threading.Thread):
    """docstring for OSCInput"""
    def __init__(self, address):
        super(OSCInput, self).__init__()
        self.address = address
        self.server = OSCServer(address)
        self.server.addMsgHandler( "default", self.default_callback )
        self.user_locations = {}

    def default_callback(self, path, tags, args, source):
        print path, args
        if path == "new_user":
            user_id = args[0]
            self.user_locations[user_id] = [0,0,0]
        elif path == "lost_user":
            user_id = args[0]
            if user_id in self.user_locations:
                self.user_locations.pop(user_id)
        elif path == "user":
            user_id = args[0]
            loc = (args[1], args[2], args[3])
            self.user_locations[user_id] = loc
        else:
            print "Unknown Path: "+str(path)

    def get_val(self, name):
        if name in self.values.keys():
            return self.values[name]
        else:
            return None

    def run(self):
        print "OSCInput: Running OSCInput"
        self.server.serve_forever()
        print "OSCInput: Thread finished"

    def close(self):
        self.server.close()
