from oscinput import OSCInput
osc = OSCInput(("0.0.0.0", 9001))
osc.start()
osc.join()
