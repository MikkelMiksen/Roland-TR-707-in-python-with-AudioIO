import audioio as AudioIO
import numpy as np
import SoundUtils

def kick(beats):
    return ("kick", beats)

def snare(beats):
    return ("snare", beats)

def ch(beats):
    return ("ch", beats)

def oh(beats):
    return ("oh", beats)


def build_beat(events, Fs, seconds_per_beat):
    total_beats = sum(beats for _, beats in events)
    total_samples = int(total_beats * seconds_per_beat * Fs)

    output = np.zeros(total_samples)
    cursor = 0

    for drum, beats in events:
        duration = beats * seconds_per_beat
        samples = int(duration * Fs)

        if drum == "kick":
            y = SoundUtils.kick(Fs, duration)
        elif drum == "snare":
            y = SoundUtils.snare(Fs, duration)
        elif drum == "ch":
            y = SoundUtils.hihat_closed(Fs, duration)
        elif drum == "oh":
            y = SoundUtils.hihat_open(Fs, duration)
        else:
            y = np.zeros(samples)

        output[cursor:cursor+samples] += y[:samples]
        cursor += samples

    return output

beat = [
    kick(0.25), ch(0.25), ch(0.25), ch(0.25),
    snare(0.5), ch(0.5),
    kick(0.5), ch(0.25), ch(0.25),
    snare(0.5), ch(0.25), ch(0.25),

    kick(0.25), ch(0.25), ch(0.25), ch(0.25),
    snare(0.5), ch(0.5),
    kick(0.5), ch(0.25), ch(0.25),
    snare(0.5), ch(0.25), ch(0.25),

    kick(0.25), ch(0.25), ch(0.25), ch(0.25),
    snare(0.5), ch(0.5),
    kick(0.5), ch(0.25), ch(0.25),
    snare(0.5), ch(0.25), ch(0.25),

    kick(0.25), ch(0.25), ch(0.25), ch(0.25),
    snare(0.5), ch(0.5),
    kick(0.5), ch(0.25), ch(0.25),
    snare(0.5), ch(0.25), ch(0.25),

    kick(0.25), ch(0.25), ch(0.25), ch(0.25),
    snare(0.5), ch(0.5),
    kick(0.5), ch(0.25), ch(0.25),
    snare(0.5), ch(0.25), ch(0.25),

    kick(0.25), ch(0.25), ch(0.25), ch(0.25),
    snare(0.5), ch(0.5),
    kick(0.5), ch(0.25), ch(0.25),
    snare(0.5), ch(0.25), ch(0.25),

    kick(0.25), ch(0.25), ch(0.25), ch(0.25),
    snare(0.5), ch(0.5),
    kick(0.5), ch(0.25), ch(0.25),
    snare(0.5), ch(0.25), ch(0.25),

    kick(0.25), ch(0.25), ch(0.25), ch(0.25),
    snare(0.5), ch(0.5),
    kick(0.5), ch(0.25), ch(0.25),
    snare(0.5), ch(0.25), ch(0.25),
]

bpm = 140
seconds_per_beat = 60 / bpm
Fs = 44100

output = build_beat(beat, Fs, seconds_per_beat)
output /= np.max(np.abs(output))
output = output.reshape(-1,1)

AudioIO.play(output, Fs)


