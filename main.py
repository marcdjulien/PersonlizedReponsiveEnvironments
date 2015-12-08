from led_state_machine import LEDStateMachine
from oscinput import OSCInput
from kinect_input import KinectInput

ART_NET_UDP_PORT = 6454

# DMX Servers to send packets to
led_dmx_address = ("10.7.158.185", ART_NET_UDP_PORT)
lights_dmx_address = ("10.7.158.190", ART_NET_UDP_PORT)
# Local OSC Server to listen for messages
osc_address = ("0.0.0.0", 9000)
# Input from Kinect address
kinect_input_address = ("0.0.0.0", 9001)

led_period = 0.01 # In seconds
osc = OSCInput(osc_address)
kinect = KinectInput(kinect_input_address)
leds = LEDStateMachine(led_period, led_dmx_address, lights_dmx_address, osc, kinect, show_gui=True)

kinect.start()
osc.start()
leds.start()

leds.join()
osc.close()
kinect.close()
osc.join()
kinect.join()

print "Program Exit"
