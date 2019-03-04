"""OpenAL playback example."""
import os
import sys
import time
import wave
from openal import al, alc

def run():
    if len (sys.argv) < 2:
        print ("Usage: %s wavefile" % os.path.basename(sys.argv[0]))
        print ("    Using an example wav file...")
        dirname = os.path.dirname(__file__)
        fname = os.path.join(dirname, "hey.wav")
    else:
        fname = sys.argv[1]

    wavefp = wave.open(fname)
    channels = wavefp.getnchannels()
    bitrate = wavefp.getsampwidth() * 8
    samplerate = wavefp.getframerate()
    wavbuf = wavefp.readframes(wavefp.getnframes())
    formatmap = {
        (1, 8) : al.AL_FORMAT_MONO8,
        (2, 8) : al.AL_FORMAT_STEREO8,
        (1, 16): al.AL_FORMAT_MONO16,
        (2, 16) : al.AL_FORMAT_STEREO16,
    }
    alformat = formatmap[(channels, bitrate)]

    device = alc.alcOpenDevice(None)
    context = alc.alcCreateContext(device, None)
    alc.alcMakeContextCurrent(context)

    source = al.ALuint(0)
    al.alGenSources(1, source)

    al.alSourcef(source, al.AL_PITCH, 1)
    al.alSourcef(source, al.AL_GAIN, 1)
    al.alSource3f(source, al.AL_POSITION, 10, 0, 0)
    al.alSource3f(source, al.AL_VELOCITY, 0, 0, 0)
    al.alSourcei(source, al.AL_LOOPING, 1)

    buf = al.ALuint(0)
    al.alGenBuffers(1, buf)

    al.alBufferData(buf, alformat, wavbuf, len(wavbuf), samplerate)
    al.alSourceQueueBuffers(source, 1, buf)
    al.alSourcePlay(source)

    state = al.ALint(0)
    al.alGetSourcei(source, al.AL_SOURCE_STATE, state)
    z = 10
    while z > -10:
        time.sleep(1)
        al.alSource3f(source, al.AL_POSITION, z, 0, 0)
        print("playing at %r" % ([z, 0, 0]))
        z -= 1
    print("done")

    al.alDeleteSources(1, source)
    al.alDeleteBuffers(1, buf)
    alc.alcDestroyContext(context)
    alc.alcCloseDevice(device)

if __name__ == "__main__":
    sys.exit(run())
