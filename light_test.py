import pysimpledmx
import time

ART_NET_UDP_PORT = 6454

# DMX Servers to send packets to
dmx_address = ("10.7.158.190", ART_NET_UDP_PORT)

dmx = pysimpledmx.DMXConnectionEthernet(dmx_address, universe=1)

#dmx.setChannel(202, 255)
dmx.render()

time.sleep(5.0)
