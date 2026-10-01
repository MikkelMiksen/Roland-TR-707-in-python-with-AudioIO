import numpy as np

Fs = 44100


# =====================================================================
# BASE CLASS
# Every filter takes a block of samples in and returns a block out.
# Filters keep their own state between blocks, so there are no clicks
# at block boundaries.
# =====================================================================
class AudioFilter:

    def process(self, block):
        raise NotImplementedError


# =====================================================================
# BIQUAD FILTER (low-pass / high-pass / band-pass)
# Coefficients from the RBJ Audio EQ Cookbook.
# Implemented as Direct Form II Transposed, which needs only two
# state variables (z1, z2) that carry over from one block to the next.
# =====================================================================
class BiquadFilter(AudioFilter):

    def __init__(self, filter_type, cutoff, q=0.707, sample_rate=Fs):
        self.filter_type = filter_type      # "lowpass", "highpass", "bandpass"
        self.sample_rate = sample_rate
        self.cutoff = cutoff
        self.q = q

        # filter memory
        self.z1 = 0.0
        self.z2 = 0.0

        # normalised coefficients
        self.b0 = 0.0
        self.b1 = 0.0
        self.b2 = 0.0
        self.a1 = 0.0
        self.a2 = 0.0

        self._update_coefficients()

    def set_cutoff(self, cutoff):
        self.cutoff = cutoff
        self._update_coefficients()

    def set_q(self, q):
        self.q = q
        self._update_coefficients()

    def _update_coefficients(self):
        # keep the cutoff safely below Nyquist, otherwise the filter blows up
        nyquist = self.sample_rate / 2.0
        cutoff = min(max(self.cutoff, 20.0), nyquist * 0.99)

        w0 = 2.0 * np.pi * cutoff / self.sample_rate
        cos_w0 = np.cos(w0)
        alpha = np.sin(w0) / (2.0 * self.q)

        if self.filter_type == "lowpass":
            b0 = (1.0 - cos_w0) / 2.0
            b1 = 1.0 - cos_w0
            b2 = (1.0 - cos_w0) / 2.0

        elif self.filter_type == "highpass":
            b0 = (1.0 + cos_w0) / 2.0
            b1 = -(1.0 + cos_w0)
            b2 = (1.0 + cos_w0) / 2.0

        elif self.filter_type == "bandpass":
            b0 = alpha
            b1 = 0.0
            b2 = -alpha

        else:
            raise ValueError("Unknown filter type: " + str(self.filter_type))

        a0 = 1.0 + alpha
        a1 = -2.0 * cos_w0
        a2 = 1.0 - alpha

        # divide everything by a0 so the difference equation has a0 = 1
        self.b0 = b0 / a0
        self.b1 = b1 / a0
        self.b2 = b2 / a0
        self.a1 = a1 / a0
        self.a2 = a2 / a0

    def process(self, block):
        output = np.zeros(len(block))

        for i in range(len(block)):
            x = block[i]

            y = self.b0 * x + self.z1

            self.z1 = self.b1 * x - self.a1 * y + self.z2
            self.z2 = self.b2 * x - self.a2 * y

            output[i] = y

        return output


# Convenience constructors, so the synth code reads nicely
def LowPass(cutoff, q=0.707):
    return BiquadFilter("lowpass", cutoff, q)


def HighPass(cutoff, q=0.707):
    return BiquadFilter("highpass", cutoff, q)


def BandPass(cutoff, q=1.0):
    return BiquadFilter("bandpass", cutoff, q)


# =====================================================================
# DISTORTION
# Soft clipping with tanh. Higher drive = more harmonics.
# Dividing by tanh(drive) keeps peaks near +-1 so the volume
# does not jump when you change the drive.
# =====================================================================
class Distortion(AudioFilter):

    def __init__(self, drive=3.0):
        self.drive = drive

    def process(self, block):
        return np.tanh(block * self.drive) / np.tanh(self.drive)


# =====================================================================
# DELAY / ECHO
# Uses a circular buffer that persists between blocks.
#   feedback : how much of the delayed signal is fed back (0 <-> <1)
#   mix      : 0 = dry only, 1 = wet only
# =====================================================================
class Delay(AudioFilter):

    def __init__(self, delay_seconds=0.3, feedback=0.4, mix=0.35, sample_rate=Fs):
        self.delay_samples = int(delay_seconds * sample_rate)
        self.feedback = feedback
        self.mix = mix

        self.buffer = np.zeros(self.delay_samples)
        self.write_index = 0

    def process(self, block):
        output = np.zeros(len(block))

        for i in range(len(block)):
            dry = block[i]

            # the oldest sample in the buffer is exactly one delay-time old
            delayed = self.buffer[self.write_index]

            self.buffer[self.write_index] = dry + delayed * self.feedback

            self.write_index += 1
            if self.write_index >= self.delay_samples:
                self.write_index = 0

            output[i] = (1.0 - self.mix) * dry + self.mix * delayed

        return output


# =====================================================================
# FILTER CHAIN
# Runs a block through each filter in order.
# =====================================================================
class FilterChain(AudioFilter):

    def __init__(self, filters=None):
        if filters is None:
            filters = []
        self.filters = filters

    def add(self, audio_filter):
        self.filters.append(audio_filter)

    def process(self, block):
        for audio_filter in self.filters:
            block = audio_filter.process(block)
        return block