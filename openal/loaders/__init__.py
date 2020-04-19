"""Utility functions for loading sounds."""
import os
import sys
import wave
import array
from itertools import chain
from ..audio import SoundData

try:
    import soundfile  # optional
except ImportError:
    soundfile = None
import numpy


__all__ = ["load_wav_file", "load_file"]


def load_wav_file(fname):
    """Loads a WAV encoded audio file into a SoundData object."""
    fp = wave.open(fname, "rb")
    channels = fp.getnchannels()
    bitrate = fp.getsampwidth() * 8
    samplerate = fp.getframerate()
    buf = fp.readframes(fp.getnframes())
    return SoundData(buf, channels, bitrate, len(buf), samplerate)


# supported extensions
# _FILEEXTENSIONS = {
#     ".wav": load_wav_file,
#     ".ogg": load_ogg_file
# }


def load_file(fname):
    """Loads an audio file into a SoundData object."""

    if soundfile:

        with open(fname, "rb") as f:
            buf, samplerate = soundfile.read(f, dtype="int16")

        lenbuf = len(buf)
        if buf.size == 0 or type(buf[0]) == numpy.int16:
            channels = 1
        else:  # contains channels
            channels = len(buf[0])
            buf = tuple(chain(*buf))
        buf = array.array("h", buf).tobytes()
        return SoundData(buf, channels, 16, lenbuf * 2, samplerate)

    else:

        if fname.lower().endswith(".wav"):
            return load_wav_file(fname)
        else:
            raise ValueError("unsupported audio file type")


def load_stream(source):
    """Loads an audio stream into a SoundData object."""
    raise NotImplementedError("not implemented yet")
