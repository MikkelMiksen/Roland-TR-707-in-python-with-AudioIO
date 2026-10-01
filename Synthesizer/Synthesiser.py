import sounddevice as sd
import numpy as np
import win32api
import threading
from SoundFilters import music_data
from FilterUtils import LowPass, FilterChain, Distortion, Delay, BandPass, HighPass

KEY_FREQs = music_data.KEY_FREQ
Fs          =   44100
AMPLITUDE   =   .5      # volume 0 <-> 1
BLOCK_SIZE  =   1024

FILTER_CHAIN = LowPass(cutoff=500, q=.7)


# --- SHARED BY THREAD   ---
active_freqs = set()
lock = threading.Lock()

phase_table = {}



def generate_saw_block(frequency, current_phase, frames):

    phase_increment = frequency / Fs

    output = np.zeros(frames)

    for i in range(frames):
        output[i] = (current_phase  * 2.0) -1.0

        current_phase += phase_increment

        if current_phase >= 1.0:
            current_phase -= 1.0

    return output, current_phase



# --- AUDIO CALLBACK ---
def audio_callback(outdata, frames, time, status):
    global phase
    with lock:
        freqs = set(active_freqs)

    if not freqs:
        outdata[:] = 0
        phase = 0.0
        return

    combined = np.zeros(frames)

    for freq in freqs:

        if freq not in phase_table:
            phase_table[freq] = 0.0

        saw_block, updated_phase = generate_saw_block(freq, phase_table[freq], frames)

        phase_table[freq] = updated_phase

        combined += saw_block

    for freq in list(phase_table.keys()):
        if freq not in freqs:
            del phase_table[freq]

    combined /= len(freqs)

    combined *= AMPLITUDE

    combined = FILTER_CHAIN.process(combined)

    outdata[:] = combined.reshape(-1,1)

# --- INPUT REGISTER
def input_loop():
    while True:

        if win32api.GetAsyncKeyState(0x1B) & 0x8000:
            break

        pressed = set()

        for key, freq in KEY_FREQs.items():
            if win32api.GetAsyncKeyState(ord(key)) & 0x8000:
                pressed.add(freq)

        with lock:
            active_freqs.clear()
            active_freqs.update(pressed)

print('synthesiser running. Press ESC to quit.')

input_thread = threading.Thread(target=input_loop, daemon=True)
input_thread.start()

with sd.OutputStream(samplerate=Fs,
                     channels=1,
                     blocksize=BLOCK_SIZE,
                     callback=audio_callback
                     ):
    input_thread.join()