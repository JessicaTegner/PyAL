#using Pyglet
from pyglet.media.drivers.openal import lib_openal as al
from pyglet.media.drivers.openal import lib_alc as alc

#using PyAL
##from openal import al, alc

#imports for sound loading and wait during example
import wave
import time
import sys
import os

class Example(object):
    def __init__(self):
    #load listener
        self.listener = listener()
    #initialize sound
        self.sound = load_sound('tone5.wav')
    #load sound player
        self.player = Player()

    #set listener position
        self.listener.position = (320,240,0)
    #set player position
        self.player.position = (0,240,0)

    #load sound into player
        self.player.add(self.sound)
    #enable loop sound so it plays forever
        self.player.loop = True
    #set rolloff factor
        self.player.rolloff = 0.01
    #play sound
        self.player.play()

    #start recording
        self.listener.rec_start()

    #capture recorded samples (and number of samples to capture)
        while len(self.listener.samplescaptured) <= 16000:
            self.listener.rec()

    #stop player
        self.player.stop()

    #stop recording
        self.listener.rec_stop()

    #load captured audio sample into a audio buffer for playback
        self.buffer = buffer_sound()
        self.buffer.load(self.listener.samplescaptured)
        self.player.remove()
        self.player.add(self.buffer)

    #play captured audio
        self.player.play()
        time.sleep(1)

    #clean up resources
        self.player.delete()
        self.sound.delete()
        self.buffer.delete()
        self.listener.delete()



#load a listener to load and play sounds.
class listener(object):
    def __init__(self):
    #load device/context/listener
        self.device = alc.alcOpenDevice(None)
        self.context = alc.alcCreateContext(self.device, None)
        alc.alcMakeContextCurrent(self.context)
        alc.alcProcessContext(self.context)
    #get list of capture devices
        self.cap_devices = self.parse(alc.alcGetString(None, alc.ALC_CAPTURE_DEVICE_SPECIFIER))
    #capture device container
        self.captureDev = None
    #main buffer
        self.samplescaptured = ''

#list available capture devices
    def get_devices(self):
        return self.parse(alc.alcGetString(None, alc.ALC_CAPTURE_DEVICE_SPECIFIER))

#set capture device
    def _set_cap(self,data=0):
        if self.captureDev != None:
            alc.alcCaptureStop(self.captureDev)
            alc.alcCaptureCloseDevice(self.captureDev)
        self.captureDev = alc.alcCaptureOpenDevice(self.cap_devices[data], 8000, al.AL_FORMAT_MONO16, 800)

#get current capture device
    def _get_cap(self):
        if self.captureDev != None:
            return self.parse(alc.alcGetString(self.captureDev, alc.ALC_CAPTURE_DEVICE_SPECIFIER))
        else:
            return None

#get default capture device
    def get_default(self):
        return self.parse(alc.alcGetString(None, alc.ALC_CAPTURE_DEFAULT_DEVICE_SPECIFIER))

#start recording
    def rec_start(self):
    #load default capture device if none loaded
        if self.captureDev == None: #capture device, sample rate, format, buffer size
            self.captureDev = alc.alcCaptureOpenDevice(None, 8000, al.AL_FORMAT_MONO16, 800)
    #start capturing audio
        alc.alcCaptureStart(self.captureDev)
    #set main buffer
        self.samplescaptured = ''

#transfer recorded audio to main buffer
    def rec(self):
        if self.captureDev != None:
            s_available = al.ALint(0)
        #capture audio
            alc.alcGetIntegerv(self.captureDev, alc.ALC_CAPTURE_SAMPLES, 1, s_available)
        #transfer captured audio data into tmp buffer, add to main buffer
            box = ' '*(s_available.value*2)
            alc.alcCaptureSamples(self.captureDev, box, s_available)
            self.samplescaptured += box

#stop recording
    def rec_stop(self):
        if self.captureDev != None:
            s_available = al.ALint(0)
        #capture audio
            alc.alcGetIntegerv(self.captureDev, alc.ALC_CAPTURE_SAMPLES, 1, s_available)
        #transfer captured audio data into tmp buffer, add to main buffer
            self.box = ' '*(s_available.value*2)
            alc.alcCaptureSamples(self.captureDev, self.box, s_available)
            self.samplescaptured += self.box
        #stop capturing audio
            alc.alcCaptureStop(self.captureDev)

#parse openal data strings
    def parse(self,data):
    #parse available devices
        stri = ['']
        dev = 0
        for a in xrange(0,100,1):
            if data[a].isalnum() or data[a].isspace():
                stri[dev] += data[a]
            else:
                if len(stri[dev]) == 0:
                    stri.pop(dev)
                    break
                else:
                    stri.append('')
                    dev += 1
        return stri

#set player position
    def _set_position(self,pos):
        self._position = pos
        x,y,z = map(int, pos)
        al.alListener3f(al.AL_POSITION, x, y, z)

    def _get_position(self):
        return self._position

#delete current listener
    def delete(self):
        alc.alcCaptureCloseDevice(self.captureDev)
        alc.alcDestroyContext(self.context)
        alc.alcCloseDevice(self.device)

    position = property(_get_position, _set_position,doc="""get/set position""")
    cap = property(_get_cap, _set_cap,doc="""get/set caputure device""")



#load and store a wav file into an openal buffer
class load_sound(object):
    def __init__(self,filename):
        self.name = filename
    #load/set wav file
        if len (sys.argv) < 2:
            print ("Usage: %s wavefile" % os.path.basename(sys.argv[0]))
            print ("    Using an example wav file...")
            dirname = os.path.dirname(os.path.realpath(__file__))
            fname = os.path.join(dirname, filename)
        else:
            fname = sys.argv[1]

        wavefp = wave.open(fname)
        channels = wavefp.getnchannels()
        bitrate = wavefp.getsampwidth() * 8
        samplerate = wavefp.getframerate()
        wavbuf = wavefp.readframes(wavefp.getnframes())
        self.duration = (len(wavbuf) / float(samplerate))/2
        self.length = len(wavbuf)
        formatmap = {
            (1, 8) : al.AL_FORMAT_MONO8,
            (2, 8) : al.AL_FORMAT_STEREO8,
            (1, 16): al.AL_FORMAT_MONO16,
            (2, 16) : al.AL_FORMAT_STEREO16,
        }
        alformat = formatmap[(channels, bitrate)]

        self.buf = al.ALuint(0)
        al.alGenBuffers(1, self.buf)
    #allocate buffer space to: buffer, format, data, len(data), and samplerate
        al.alBufferData(self.buf, alformat, wavbuf, len(wavbuf), samplerate)

#delete loaded sound
    def delete(self):
        al.alDeleteBuffers(1, self.buf)



#OpenAL Sound Buffer
class buffer_sound(object):
    def __init__(self):
        self.channels = 1
        self.bitrate = 16
        self.samplerate = 8000
        self.wavbuf = None
        self.alformat = al.AL_FORMAT_MONO16
        self.length = None
##        formatmap = {
##            (1, 8) : al.AL_FORMAT_MONO8,
##            (2, 8) : al.AL_FORMAT_STEREO8,
##            (1, 16): al.AL_FORMAT_MONO16,
##            (2, 16) : al.AL_FORMAT_STEREO16,
##        }
##        alformat = formatmap[(channels, bitrate)]


        self.buf = al.ALuint(0)
        al.alGenBuffers(1, self.buf)

    def load(self,data):
        self.wavbuf = data
        self.length = len(data)
    #allocate buffer space to: buffer, format, data, len(data), and samplerate
        al.alBufferData(self.buf, self.alformat, self.wavbuf, len(self.wavbuf), self.samplerate)

    def delete(self):
        al.alDeleteBuffers(1, self.buf)


#load sound buffers into an openal source player to play them
class Player(object):
#load default settings
    def __init__(self):
    #load source player
        self.source = al.ALuint(0)
        al.alGenSources(1, self.source)
    #disable rolloff factor by default
        al.alSourcef(self.source, al.AL_ROLLOFF_FACTOR, 0)
    #disable source relative by default
        al.alSourcei(self.source, al.AL_SOURCE_RELATIVE,0)
    #capture player state buffer
        self.state = al.ALint(0)
    #set internal variable tracking
        self._volume = 1.0
        self._pitch = 1.0
        self._position = [0,0,0]
        self._rolloff = 1.0
        self._loop = False
        self.queue = []


#set rolloff factor, determines volume based on distance from listener
    def _set_rolloff(self,value):
        self._rolloff = value
        al.alSourcef(self.source, al.AL_ROLLOFF_FACTOR, value)

    def _get_rolloff(self):
        return self._rolloff


#set whether looping or not - true/false 1/0
    def _set_loop(self,lo):
        self._loop = lo
        al.alSourcei(self.source, al.AL_LOOPING, lo)

    def _get_loop(self):
        return self._loop
      

#set player position
    def _set_position(self,pos):
        self._position = pos
        x,y,z = map(int, pos)
        al.alSource3f(self.source, al.AL_POSITION, x, y, z)

    def _get_position(self):
        return self._position
        

#set pitch - 1.5-0.5 float range only
    def _set_pitch(self,pit):
        self._pitch = pit
        al.alSourcef(self.source, al.AL_PITCH, pit)

    def _get_pitch(self):
        return self._pitch

#set volume - 1.0 float range only
    def _set_volume(self,vol):
        self._volume = vol
        al.alSourcef(self.source, al.AL_GAIN, vol)

    def _get_volume(self):
        return self._volume

#queue a sound buffer
    def add(self,sound):
        al.alSourceQueueBuffers(self.source, 1, sound.buf) #self.buf
        self.queue.append(sound)

#remove a sound from the queue (detach & unqueue to properly remove)
    def remove(self):
        if len(self.queue) > 0:
            al.alSourceUnqueueBuffers(self.source, 1, self.queue[0].buf) #self.buf
            al.alSourcei(self.source, al.AL_BUFFER, 0)
            self.queue.pop(0)

#play sound source
    def play(self):
        al.alSourcePlay(self.source)

#get current playing state
    def playing(self):
        al.alGetSourcei(self.source, al.AL_SOURCE_STATE, self.state)
        if self.state.value == al.AL_PLAYING:
            return True
        else:
            return False

#stop playing sound
    def stop(self):
        al.alSourceStop(self.source)

#rewind player
    def rewind(self):
        al.alSourceRewind(self.source)

#pause player
    def pause(self):
        al.alSourcePause(self.source)

#delete sound source
    def delete(self):
        al.alDeleteSources(1, self.source)

#Go straight to a set point in the sound file
    def _set_seek(self,offset):#float 0.0-1.0
        al.alSourcei(self.source,al.AL_BYTE_OFFSET,int(self.queue[0].length * offset))

#returns current buffer length position (IE: 21000), so divide by the buffers self.length
    def _get_seek(self):#returns float 0.0-1.0
        al.alGetSourcei(self.source, al.AL_BYTE_OFFSET, self.state)
        return float(self.state.value)/float(self.queue[0].length)

    rolloff = property(_get_rolloff, _set_rolloff,doc="""get/set rolloff factor""")
    volume = property(_get_volume, _set_volume,doc="""get/set volume""")
    pitch = property(_get_pitch, _set_pitch, doc="""get/set pitch""")
    loop = property(_get_loop, _set_loop, doc="""get/set loop state""")
    position = property(_get_position, _set_position,doc="""get/set position""")
    seek = property(_get_seek, _set_seek, doc="""get/set the current play position""")



Example()
