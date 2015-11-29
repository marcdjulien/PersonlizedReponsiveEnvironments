from led_state_machine import LEDStateMachine
#from light_state_machine import LightStateMachine
from oscinput import OSCInput
#from kinect_input import KinectInput

ART_NET_UDP_PORT = 6454

# DMX Server to send packets to
led_dmx_address = ("10.7.158.185", ART_NET_UDP_PORT)
# Local OSC Server to listen for messages
osc_address = ("0.0.0.0", 9000)

led_period = 0.050 # In seconds
osc = OSCInput(osc_address)
#kinect = KinectInput()
leds = LEDStateMachine(led_period, led_dmx_address, osc, show_gui=True)
#lights - LightStateMachine(light_period, light_dmx_address, osc)

osc.start()
leds.start()
#light.starts()

leds.join()
#lights.join()
osc.server.close()
osc.join()

print "Program Exit"
