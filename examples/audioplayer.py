"""OpenAL playback example."""
import os
import sys
import time

try:
    import openal
except ImportError:
    sys.path.append("..")
from openal.audio import SoundSink, SoundSource
from openal.loaders import load_file


def run():
    if len(sys.argv) < 2:
        print("Usage: %s soundfile" % os.path.basename(sys.argv[0]))
        print("    Using an example wav file...")
        dirname = os.path.dirname(__file__)
        fname = os.path.join(dirname, "hey.wav")
    else:
        fname = sys.argv[1]

    sink = SoundSink()
    sink.activate()

    source = SoundSource(position=[10, 0, 0])
    source.looping = True

    data = load_file(fname)
    source.queue(data)

    sink.play(source)
    while source.position[0] > -10:
        source.position = [
            source.position[0] - 1,
            source.position[1],
            source.position[2],
        ]
        sink.update()
        print("playing at %r" % source.position)
        time.sleep(2)
    print("done")


if __name__ == "__main__":
    sys.exit(run())
