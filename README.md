# python-pitch-detection
Rudimentary live pitch detection in Python using PyAduio


Reading input from a microphone, uses autocorrelation on the signal to determine the main frequency.

This method produces a lot of false readings due to microphone noise and signal clarity, so the readings are averaged over time.

Best demonstration is to whistle into the microphone to produce a clear strong signal.


The script:

• Reads a chunk of input from the microphone

• Decodes the raw byte data into integer values

• Smooths the data with a weighted average

• Autocorrelates the data to find the lowest difference time offsets with itself

• Averages the offsets to remove possible errors

• Uses the average time offset to determine the main frequency of the signal
