import pyaudio
import time
import numpy as np
import math
import matplotlib.pyplot as plt

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 64000
CHUNK = 1024	# 1024

all_pitches = []

stream_buffer = []

p = pyaudio.PyAudio()

def empty_frame(length):
	"""Returns an empty 16bit audio frame of supplied length."""
	frame = np.zeros(length, dtype='i2')
	return to_raw_data(frame)

def callback_in(in_data, frame_count, time_info, status):
	"""Callback function for incoming data from an input stream."""
	stream_buffer.append(in_data)
	process(in_data)
	return (in_data, pyaudio.paContinue)

def callback_out(in_data, frame_count, time_info, status):
	"""Callback function for outgoing data to an output stream."""
	try:
		data = stream_buffer.pop(0)
	except:
		data = empty_frame(frame_count)
	return (data, pyaudio.paContinue)

def to_int_data(raw_data):
	"""Converts raw bytes data to ."""
	return np.array([int.from_bytes(raw_data[i:i+2], byteorder='little', signed=True) for i in range(0, len(raw_data), 2)])

def to_raw_data(int_data):
	data = int_data.clip(-32678, 32677)
	data = data.astype(np.dtype('i2'))
	return b''.join(data.astype(np.dtype('V2')))

def process(raw_data):
	st = time.time()
	data = to_int_data(raw_data)
	data = data*4		# raise volume
	detect_pitch(data)
	et = time.time()
	return to_raw_data(data)

def normal_distribution(w):
	width = w+1
	weights = np.exp(-np.square([2*x/width for x in range(width)]))
	weights = np.pad(weights, (width-1,0), 'reflect')
	weights = weights/np.sum(weights)
	return weights

def detect_pitch(int_data):
	if 'avg' not in detect_pitch.__dict__:
		detect_pitch.avg = 0
	WIND = 10
	CYCLE = 400
	weights = normal_distribution(WIND)
	windowed_data = np.pad(int_data, WIND, 'reflect')
	smooth_data = np.convolve(int_data, weights, mode='valid')
	smooth_pitches = [0]+[np.mean(smooth_data[:-delay] - smooth_data[delay:]) for delay in range(1,CYCLE)]

	dips = [x for x in range(WIND, CYCLE-WIND) if smooth_pitches[x] == np.min(smooth_pitches[x-WIND:x+WIND])]
	if len(dips) > 1:
		av_dip = np.mean(np.ediff1d(dips))
		cheq_freq = RATE / av_dip
		detect_pitch.avg = detect_pitch.avg*0.5 + cheq_freq*0.5
		all_pitches.append(int(detect_pitch.avg))
		print('\r'+str(int(detect_pitch.avg))+' Hz        ', end='')


if __name__ == "__main__":
	stream_in = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, stream_callback=callback_in)
	stream_out = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, stream_callback=callback_out)

	stream_in.start_stream()
	stream_out.start_stream()

	txt = input()	#stream until enter key press

	stream_in.stop_stream()
	stream_in.close()
	stream_out.stop_stream()
	stream_out.close()

	p.terminate()

	plt.plot(all_pitches)
	plt.show()