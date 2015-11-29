import socket
import struct
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", 10000))
print "starting"
data, addr = sock.recvfrom(1024)
print struct.unpack("c"*len(data), data)
print addr
