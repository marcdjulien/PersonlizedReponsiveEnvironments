from OSC import OSCServer
import sys
from time import sleep

server = OSCServer( ("localhost", 7110) )
server.timeout = 0
run = True

# this method of reporting timeouts only works by convention
# that before calling handle_request() field .timed_out is 
# set to False
def handle_timeout(self):
    self.timed_out = True

# funny python's way to add a method to an instance of a class
import types
server.handle_timeout = types.MethodType(handle_timeout, server)

def user_callback(path, tags, args, source):
    print "ADSF"
    # which user will be determined by path:
    # we just throw away all slashes and join together what's left
    user = ''.join(path.split("/"))
    # tags will contain 'fff'
    # args is a OSCMessage with data
    # source is where the message came from (in case you need to reply)
    print ("Now do something with", args) 

def quit_callback(path, tags, args, source):
    # don't do this at home (or it'll quit blender)
    global run
    run = False

def default(path, tags, args, source):
    print path

server.addMsgHandler( "default", default )
server.addMsgHandler( "/1/fader1", user_callback )
server.addMsgHandler( "/1/fader2", user_callback )
server.addMsgHandler( "/1/fader3", user_callback )
server.addMsgHandler( "/1/fader4", user_callback )
server.addMsgHandler( "/1/fader5", user_callback )
server.addMsgHandler( "/quit", quit_callback )

# user script that's called by the game engine every frame
def each_frame():
    # clear timed_out flag
    server.timed_out = False
    # handle all pending requests then return
    while not server.timed_out:
        server.handle_request()

print server.address()
# simulate a "game engine"
while run:
    # do the game stuff
    sleep(1)
    # call user script
    each_frame()

server.close()