import json
import numpy as np
ROWS = 5
COLS = 6

ADJUST_ARRAY = [[0.2, 0.4, 0.6, 0.6, 0.4, 0.2],
                [0.4, 0.6, 0.8, 0.8, 0.6, 0.4],
                [0.6, 0.8, 1.0, 1.0, 0.8, 0.6],
                [0.4, 0.6, 0.8, 0.8, 0.6, 0.4],
                [0.2, 0.4, 0.6, 0.6, 0.4, 0.2]]

def custom_sort(a, b):
	a1 = a.split("::")[1]
	a1 = int(a1.split("-")[0])
	b1 = b.split("::")[1]
	b1 = int(b1.split("-")[0])
	return a1 - b1


def ledjson_to_array(json_filename, index=None):
	f = open(json_filename, "r")
	json_data = json.load(f)
	if not index:
		index = 1
	led_data = json_data['pattrstorage']['slots'][str(index)]["data"]
	keys = led_data.keys()
	keys.sort(custom_sort)
	led_array = np.empty((ROWS, COLS, 3))
	i = 0
	for key in keys:
		if "rgb" in key:
			led_array[i/COLS, i % COLS, :] = np.array(led_data[key])
			i+=1
			print i
	return led_array.astype(np.int)

NIGHT_LEDS = ledjson_to_array("night_leds.json", 8)
MORNING_LEDS = ledjson_to_array("morning_leds.json", 8)
NEUTRAL_LEDS = ledjson_to_array("neutral.json", 1)
