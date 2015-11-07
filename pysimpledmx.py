import sys
import socket

START_VAL   = 0x7E
END_VAL     = 0xE7

COM_BAUD    = 57600
COM_TIMEOUT = 1
COM_PORT    = 7
DMX_SIZE    = 512

LABELS = {
         'GET_WIDGET_PARAMETERS' :3,  #unused
         'SET_WIDGET_PARAMETERS' :4,  #unused
         'RX_DMX_PACKET'         :5,  #unused
         'TX_DMX_PACKET'         :6,
         'TX_RDM_PACKET_REQUEST' :7,  #unused
         'RX_DMX_ON_CHANGE'      :8,  #unused
      }

class DMXConnection(object):
  def __init__(self, comport = None):
    '''
    On Windows, the only argument is the port number. On *nix, it's the path to the serial device.
    For example:
        DMXConnection(4)              # Windows
        DMXConnection('/dev/tty2')    # Linux
        DMXConnection("/dev/ttyUSB0") # Linux
    '''
    self.dmx_frame = [0] * DMX_SIZE
    try:
      self.com = serial.Serial(comport, baudrate = COM_BAUD, timeout = COM_TIMEOUT)
    except:
      com_name = 'COM%s' % (comport + 1) if type(comport) == int else comport
      print "Could not open device %s. Quitting application." % com_name
      sys.exit(0)

    print "Opened %s." % (self.com.portstr)


  def setChannel(self, chan, val, autorender = False):
    '''
    Takes channel and value arguments to set a channel level in the local
    DMX frame, to be rendered the next time the render() method is called.
    '''
    if not 1 <= chan <= DMX_SIZE:
      print 'Invalid channel specified: %s' % chan-1
      return
    # clamp value
    val = max(0, min(val, 255))
    self.dmx_frame[chan-1] = val
    if autorender: self.render()

  def clear(self, chan = 0):
    '''
    Clears all channels to zero. blackout.
    With optional channel argument, clears only one channel.
    '''
    if chan == 0:
      self.dmx_frame = [0] * DMX_SIZE
    else:
      self.dmx_frame[chan-1] = 0




class DMXConnectionEthernet(DMXConnection):
    def __init__(self, address):
        '''
        For example:
            DMXConnection(("localhost", 8000))
        '''
        self.dmx_frame = [0] * DMX_SIZE
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.address = address
        except Exception, e:
          print "Could not create socket for %s,%d. Quitting application." % address
          print e
          sys.exit(0)

        print "Socket created %s,%d." % (self.address)

    def render(self):
        ''''
        Updates the DMX output from the USB DMX Pro with the values from self.dmx_frame.
        '''
        header = ["A", "r", "t", "-", "N", "e", "t", 0, 0x50, 0x00, ]
        packet = struct.pack("cccccccccccccccccc", *header)
        packet += map(chr, self.dmx_frame) 
        print "Bytes sent: %d"%(self.socket.sendto(packet, self.address))