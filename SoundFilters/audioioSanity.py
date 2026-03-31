import numpy as np
import sounddevice as sd

Fs = 44100
t = np.linspace(0, 1, Fs, endpoint=False)
tone = np.sin(2*np.pi*440*t)

sd.play(tone, Fs)
sd.wait()