import numpy as np
import audioio

Fs = 44100
t = np.linspace(0, 1, Fs, endpoint=False)

tone = np.sin(2*np.pi*440*t).astype(np.float32)
tone = tone.reshape(-1, 1)

audioio.play(tone, Fs)