import socket
import struct
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("", 8000))
print "starting"
data, addr = sock.recvfrom(1024)
print struct.unpack("c"*len(data), data)
print addr
