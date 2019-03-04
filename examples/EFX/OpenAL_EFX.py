#using Pyglet
from pyglet.media.drivers.openal import lib_openal as al
from pyglet.media.drivers.openal import lib_alc as alc
from pyglet.media.drivers.openal import lib_efx as efx

#using PyAL
##from openal import al, alc, efx

#imports for sound loading and wait during example
import wave
import time
import sys
import os


#For more information on EFX Extentions and how to use them, check out the
#OpenAL Effect Extentions Guide:

#http://kcat.strangesoft.net/misc-downloads/Effects%20Extension%20Guide.pdf


class Example(object):
    def __init__(self):
    #load EFX listener
        self.listener = EFX_listener()
    #initialize sound
        self.sound = load_sound('LQ_Snare Rev.wav')
    #load EFX sound player
        self.player = EFX_Player()

    #create an EFX slot for effects
        self.slot = EFXslot()
    #create a reverb effect
        self.effect1 = reverb()
    #mount the effect into the EFX slot
        self.slot.set_effect(self.effect1)

    #create a filter effect
        self.filter1 = bandpass_filter()
        self.filter1.gain = 0.5
        
    #set listener position
        self.listener.position = (320,240,0)
    #set player position
        self.player.position = (160,240,0)

    #load sound into player
        self.player.add(self.sound)
    #set rolloff factor
        self.player.rolloff = 0.01


    #move sound from left to right
        for a in range(0,15,1):
            if a == 5:
            #connect a source to output through the EFX slot to apply the effect
                self.player.add_effect(self.slot)
            elif a == 10:
            #attach a direct filter to the source
                self.player.add_filter(self.filter1)

            self.player.play()
            time.sleep(1)

    #stop player
        self.player.stop()

    #clean up resources
        self.effect1.delete()
        self.filter1.delete()
        self.player.delete()
        self.slot.delete()
        self.sound.delete()
        self.listener.delete()
        


#EFX slot for playing effects
class EFXslot(object):
    def __init__(self):
        self.slot = al.ALuint(0)
        efx.alGenAuxiliaryEffectSlots(1,self.slot)
        self._effect = None

#set master volume of effect slot
    def gain(self,data):
        efx.alAuxiliaryEffectSlotf(self.slot,efx.AL_EFFECTSLOT_GAIN, data)

#toggle automatic send adjustments based on locations of sources and listeners
    def send_auto(self,data):
        efx.alAuxiliaryEffectSloti(self.slot, efx.AL_EFFECTSLOT_AUXILIARY_SEND_AUTO, data)#al.AL_TRUE

#load/unload effect from auxiliary effect slots
    def set_effect(self,effect):
    #unload effect from slot
        if effect == None:
            if self._effect != None:
                try:
                    efx.alAuxiliaryEffectSloti(self.slot,efx.AL_EFFECTSLOT_EFFECT,efx.AL_EFFECT_NULL)
                    self._effect = None
                except:
                    print('ERROR: cant remove effect from effect slot')

    #load effect into slot
        elif efx.alIsEffect(effect.effect):
            try:
                efx.alAuxiliaryEffectSloti(self.slot,efx.AL_EFFECTSLOT_EFFECT,effect.effect.value)
                self._effect = effect
            except:
                print('ERROR: cant attach effect to effect slot')

#clean up resources
    def delete(self):
        self.set_effect(None)

#causes access error with pyglet, fine with PyAL
##        efx.alDeleteAuxiliaryEffectSlots(1,self.slot)
        al.alDeleteBuffers(1, self.slot)





#load a listener to load and play sounds.
class EFX_listener(object):
    def __init__(self):
    #load device/context/listener
        self.device = alc.alcOpenDevice(None)
        self.context = alc.alcCreateContext(self.device, None)
        alc.alcMakeContextCurrent(self.context)
        self.mpu = 1.0

#set player position
    def _set_position(self,pos):
        self._position = pos
        x,y,z = map(int, pos)
        al.alListener3f(al.AL_POSITION, x, y, z)

    def _get_position(self):
        return self._position
#min le-37, max le+37, default 1.0
    def _set_meters_per_unit(self,data):
        al.alListenerf(al.AL_METERS_PER_UNIT,data)
        self.mpu = data

    def _get_meters_per_unit(self):
        return self.mpu

#delete current listener
    def delete(self):
        alc.alcDestroyContext(self.context)
        alc.alcCloseDevice(self.device)

    position = property(_get_position, _set_position,doc="""get/set position""")
    meters_per_unit = property(_get_meters_per_unit, _set_meters_per_unit, doc="""for setting air absorption properties""")




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





#load sound buffers into an openal source player to play them
class EFX_Player(object):
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
        self._filter = []
        self._effect = []
        self._absorption = 0.0
        self._room_rolloff = 0.0
        self._outer_gainhf = 1.0
        self._min_dfilter_gainhf = True
        self._min_aux_filter_gain_auto = True
        self._min_aux_filter_gainhf_auto = True


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


#Go straight to a set point in the sound file, uses 0.0-1.0 float value
    def seek(self,offset):
        al.alSourcei(self.source,al.AL_BYTE_OFFSET,int(self.queue[0].length * offset))

#attach source to an auxiliary effects slot (with or without filter)
    def add_effect(self,slot,filtr=None):
        if filtr == None:
            try:
                al.alSource3i(self.source, efx.AL_AUXILIARY_SEND_FILTER, slot.slot.value,0,efx.AL_EFFECT_NULL)
                self._effect.append(slot)
            except:
                print('ERROR: cant connect source to effect slot')
        else:
            try:
                al.alSource3i(self.source, efx.AL_AUXILIARY_SEND_FILTER, slot.slot.value,1,filtr.filter.value)
                self._effect.append(slot)
            except:
                print('ERROR: cant connect source/filter to effect slot')

#remove source from an auxiliary effects slot (filter and all)
    def del_effect(self,slot):
        try:
            al.alSource3i(self.source, efx.AL_AUXILIARY_SEND_FILTER, efx.AL_EFFECTSLOT_NULL,0,efx.AL_EFFECT_NULL)
            self._effect.remove(slot)
        except:
            print('ERROR: cant remove source from effect slot')

#add a direct (dry) filter on source
    def add_filter(self,filtr):
        if filtr not in self._filter:
            al.alSourcei(self.source, efx.AL_DIRECT_FILTER, filtr.filter.value)
            self._filter.append(filtr)

#remove a direct (dry) filter from source
    def del_filter(self,filtr):
        if filtr in self._filter:
            al.alSourcei(self.source, efx.AL_DIRECT_FILTER, efx.AL_FILTER_NULL)
            self._filter.remove(filtr)

#min 0.0, max 10.0, default 0.0
    def _set_air_absorption_factor(self,data):
        if data >= 0.0 and data <= 10.0:
            al.alSourcef(self.source, efx.AL_AIR_ABSORPTION_FACTOR, data)
            self._absorption = data

    def _get_air_absorption_factor(self):
        return self._absorption

#min 0.0, max 10.0, default 0.0
    def _set_room_rolloff_factor(self,data):
        if data >= 0.0 and data <= 10.0:
            al.alSourcef(self.source, efx.AL_ROOM_ROLLOFF_FACTOR, data)
            self._room_rolloff = data

    def _get_room_rolloff_factor(self):
        return self._room_rolloff

#min 0.0, max 1.0, default 1.0
    def _set_cone_outer_gainhf(self,data):
        if data >= 0.0 and data <= 1.0:
            al.alSourcef(self.source, efx.AL_CONE_OUTER_GAINHF, data)
            self._outer_gainhf = data

    def _get_cone_outer_gainhf(self):
        return self._outer_gainhf

#default True
    def _set_min_direct_filter_gainhf(self,data):
        if data == False or data == True:
            al.alSourcef(self.source, efx.AL_MIN_DIRECT_FILTER_GAINHF, data)
            self._min_dfilter_gainhf = data

    def _get_min_direct_filter_gainhf(self):
        return self._min_dfilter_gainhf

#default True
    def _set_min_auxiliary_send_filter_gain_auto(self,data):
        if data == False or data == True:
            al.alSourcef(self.source, efx.AL_MIN_AUXILIARY_SEND_FILTER_GAIN_AUTO, data)
            self._min_aux_filter_gain_auto = data

    def _get_min_auxiliary_send_filter_gain_auto(self):
        print self._min_aux_filter_gain_auto

#default True
    def _set_min_auxiliary_send_filter_gainhf_auto(self,data):
        if data == False or data == True:
            al.alSourcef(self.source, efx.AL_MIN_AUXILIARY_SEND_FILTER_GAINHF_AUTO, data)
            self._min_aux_filter_gainhf_auto = data

    def _get_min_auxiliary_send_filter_gainhf_auto(self):
        print self._min_aux_filter_gainhf_auto

#delete sound source
    def delete(self):
        for a in self._effect:
            self.del_effect(a)
        for a in self._filter:
            self.del_filter(a)
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
    air_absorption_factor = property(_get_air_absorption_factor, _get_air_absorption_factor, doc="""get/set air absorption factor""")
    room_rolloff_factor = property(_get_room_rolloff_factor, _set_room_rolloff_factor, doc="""get/set room rolloff factor""")
    cone_outer_gainhf = property(_get_cone_outer_gainhf, _set_cone_outer_gainhf, doc="""get/set cone outer gainhf""")
    min_direct_filter_gainhf = property(_get_min_direct_filter_gainhf, _set_min_direct_filter_gainhf, doc="""get/set min direct filter gainhf""")
    min_auxiliary_send_filter_gain_auto = property(_get_min_auxiliary_send_filter_gain_auto, _set_min_auxiliary_send_filter_gain_auto, doc="""get/set auxiliary send gain auto""")
    min_auxiliary_send_filter_gainhf_auto = property(_get_min_auxiliary_send_filter_gainhf_auto, _set_min_auxiliary_send_filter_gainhf_auto, doc="""get/set auxiliary send gainhf auto""")



#effects
#---------------------------------------------------------------------|
#echo effect
class reverb(object):
    def __init__(self):
    #log defaults
        self._density = 1.0
        self._diffusion = 1.0
        self._gain = 0.32
        self._gainhf = 0.89
        self._decay_time = 1.49
        self._hfratio = 0.83
        self._reflections_gain = 0.05
        self._reflections_delay = 0.007
        self._late_reverb_gain = 1.26
        self._late_reverb_delay = 0.011
        self._air_absorption_gainhf = 0.994
        self._room_rolloff_factor = 0.0
        self._decay_hflimit = True

    #allocate buffer
        self.effect = al.ALuint(0)

    #generate effect
        try:
            efx.alGenEffects(1,self.effect)
        except:
            print('ERROR: cant generate reverb effect')

    #set effect to reverb
        efx.alEffecti(self.effect, efx.AL_EFFECT_TYPE, efx.AL_EFFECT_REVERB)


#set reverb density: min 0.0, max 1.0, default 1.0
    def _set_density(self,data):
        efx.alEffectf(self.effect, efx.AL_REVERB_DENSITY, data)
        self._density = data

    def _get_density(self):
        return self._density

#set reverb diffusion: min 0.0, max 1.0, default 1.0
    def _set_diffusion(self,data):
        efx.alEffectf(self.effect, efx.AL_REVERB_DIFFUSION, data)
        self._diffusion = data

    def _get_diffusion(self):
        return self._diffusion

#set reverb gain: min 0.0, max 1.0, default 0.32
    def _set_gain(self,data):
        efx.alEffectf(self.effect, efx.AL_REVERB_GAIN, data)
        self._gain = data

    def _get_gain(self):
        return self._gain

#min 0.0, max 1.0, default 0.89
    def _set_gainhf(self,data):
        efx.alEffectf(self.effect, efx.AL_REVERB_GAINHF, data)
        self._gainhf = data

    def _get_gainhf(self):
        return self._gainhf

#set reverb decay time: min 0.1, max 20.0, default 1.49
    def _set_decay_time(self,data):
        efx.alEffectf(self.effect, efx.AL_REVERB_DECAY_TIME, data)
        self._decay_time = data

    def _get_decay_time(self):
        return self._decay_time

#min 0.1, max 2.0, default 0.83
    def _set_hfratio(self,data):
        efx.alEffectf(self.effect, efx.AL_REVERB_DECAY_HFRATIO, data)
        self._hfratio = data

    def _get_hfratio(self):
        return self._hfratio

#min 0.0, max 3.16, default 0.05
    def _set_reflections_gain(self,data):
        efx.alEffectf(self.effect, efx.AL_REVERB_REFLECTIONS_GAIN, data)
        self._reflections_gain = data

    def _get_reflections_gain(self):
        return self._reflections_gain

#min 0.0, max 0.3, default 0.007
    def _set_reflections_delay(self,data):
        efx.alEffectf(self.effect, efx.AL_REVERB_REFLECTIONS_DELAY, data)
        self._reflections_delay = data

    def _get_reflections_delay(self):
        return self._reflections_delay

#min 0.0, max 10.0, default 1.26
    def _set_late_reverb_gain(self,data):
        efx.alEffectf(self.effect, efx.AL_REVERB_LATE_REVERB_GAIN, data)
        self._late_reverb_gain = data

    def _get_late_reverb_gain(self):
        return self._late_reverb_gain

#min 0.0, max 01, default 0.011
    def _set_late_reverb_delay(self_data):
        efx.alEffectf(self.effect, efx.AL_REVERB_LATE_REVERB_DELAY, data)
        self._late_reverb_delay = data

    def _get_late_reverb_delay(self):
        return self._late_reverb_delay

#min 0.892, max 1.0, default 0.994
    def _set_air_absorption_gainhf(self,data):
        efx.alEffectf(self.effect, efx.AL_REVERB_AIR_ABSORPTION_GAINHF, data)
        self._air_absorption_gainhf = data

    def _get_air_absorption_gainhf(self):
        return self._air_absorption_gainhf

#min 0.0, max 10.0, default 0.0
    def _set_room_rolloff_factor(self,data):
        efx.alEffectf(self.effect, efx.AL_REVERB_ROOM_ROLLOFF_FACTOR, data)
        self._room_rolloff_factor = data

    def _get_room_rolloff_factor(self):
        return self._room_rolloff_factor

#min AL_False, max AL_True, default AL_True
    def _set_decay_hflimit(self):
        efx.alEffectf(self.effect, efx.AL_REVERB_DECAY_HFLIMIT, data)
        self._decay_hflimit = data

    def _get_decay_hflimit(self):
        return self._decay_hflimit

#clean up resources
    def delete(self):
        efx.alDeleteEffects(1,self.effect)

    density = property(_get_density, _set_density,doc="""get/set density""")
    diffusion = property(_get_diffusion, _set_diffusion,doc="""get/set diffusion""")
    gain = property(_get_gain, _set_gain, doc="""get/set gain""")
    gainhf = property(_get_gainhf, _set_gainhf, doc="""get/set gainhf""")
    decay_time = property(_get_decay_time, _set_decay_time, doc="""get/set decay time""")
    hfratio = property(_get_hfratio, _set_hfratio, doc="""get/set hfratio""")
    reflections_gain = property(_get_reflections_gain, _set_reflections_gain, doc="""get/set reflections gain""")
    reflections_delay = property(_get_reflections_delay, _set_reflections_delay, doc="""get/set reflections delay""")
    late_reverb_gain = property(_get_late_reverb_gain, _set_late_reverb_gain, doc="""get/set late reverb gain""")
    late_reverb_delay = property(_get_late_reverb_delay, _set_late_reverb_delay, doc="""get/set late reverb delay""")
    air_absorption_gainhf = property(_get_air_absorption_gainhf, _set_air_absorption_gainhf, doc="""get/set air absorption gainhf""")
    room_rolloff_factor = property(_get_room_rolloff_factor, _set_room_rolloff_factor, doc="""get/set room rolloff factor""")
    decay_hflimit = property(_get_decay_hflimit, _set_decay_hflimit, doc="""get/set decay hflimit""")
    
    




class EAXreverb(object):
    def __init__(self):
    #log defaults
        self._density = 1.0
        self._diffusion = 1.0
        self._gain = 0.32
        self._gainhf = 0.89
        self._gainlf = 1.0
        self._decay_time = 1.49
        self._decay_hfratio = 0.83
        self._decay_lfratio = 1.0
        self._reflections_gain = 0.05
        self._reflections_delay = 0.007
        self._reflections_pan = 0.0
        self._late_reverb_gain = 1.26
        self._late_reverb_delay = 0.011
        self._late_reverb_pan = 0.0
        self._echo_time = 0.25
        self._echo_depth = 0.0
        self._modulation_time = 0.25
        self._modulation_depth = 0.0
        self._air_absorption_gainhf = 0.994
        self._hfreference = 5000.0
        self._lfreference = 250.0
        self._room_rolloff_factor = 0.0
        self._decay_hflimit = True
    #allocate buffer
        self.effect = al.ALuint(0)

    #generate effect
        try:
            efx.alGenEffects(1,self.effect)
        except:
            print('ERROR: cant generate EAXreverb effect')

    #set effect to echo
        efx.alEffecti(self.effect, efx.AL_EFFECT_TYPE, efx.AL_EFFECT_EAXREVERB)

#min 0,0, max 1.0, default 1.0
    def _set_density(self,data):
        efx.alEffectf(self.effect, efx.AL_EAXREVERB_DENSITY, data)
        self._density = data

    def _get_density(self):
        return self._density

#min 0.0, max 1.0, default 1.0
    def _set_diffusion(self,data):
        efx.alEffectf(self.effect, efx.AL_EAXREVERB_DIFFUSION, data)
        self._diffusion = data

    def _get_diffusion(self):
        return self._diffusion

#min 0.0, max 1.0, default 0.32
    def _set_gain(self,data):
        efx.alEffectf(self.effect, efx.AL_EAXREVERB_GAIN, data)
        self._gain = data

    def _get_gain(self):
        return self._gain

#min 0.0, max 1.0, default 0.89
    def _set_gainhf(self,data):
        efx.alEffectf(self.effect, efx.AL_EAXREVERB_GAINHF, data)
        self._gainhf = data

    def _get_gainhf(self):
        return self._gainhf

#min 0.0, max 1.0, default 1.0
    def _set_gainlf(self,data):
        efx.alEffectf(self.effect, efx.AL_EAXREVERB_GAINLF, data)
        self._gainlf = data

    def _get_gainlf(self):
        return self._gainlf

#min 0.1, max 20.0, default 1.49
    def _set_decay_time(self,data):
        efx.alEffectf(self.effect, efx.AL_EAXREVERB_DECAY_TIME, data)
        self._decay_time = data

    def _get_decay_time(self):
        return self._decay_time

#min 0.1, max 2.0, default 0.83
    def _set_decay_hfratio(self,data):
        efx.alEffectf(self.effect, efx.AL_EAXREVERB_DECAY_HFRATIO, data)
        self._decay_hfratio = data

    def _get_decay_hfratio(self):
        return self._decay_hfratio

#min 0.1, max 2.0, default 1.0
    def _set_decay_lfratio(self,data):
        efx.alEffectf(self.effect, efx.AL_EAXREVERB_DECAY_LFRATIO, data)
        self._decay_lfratio = data

    def _get_decay_lfratio(self):
        return self._decay_lfratio

#min 0.0, max 3.16, default 0.05
    def _set_reflections_gain(self,data):
        efx.alEffectf(self.effect, efx.AL_EAXREVERB_REFLECTIONS_GAIN, data)
        self._reflections_gain = data

    def _get_reflections_gain(self):
        return self._reflections_gain

#min 0.0, max 0.3, default 0.007
    def _set_reflections_delay(self,data):
        efx.alEffectf(self.effect, efx.AL_EAXREVERB_REFLECTIONS_DELAY, data)
        self._reflections_delay = data

    def _get_reflections_delay(self):
        return self._reflections_delay

#default 0.0
    def _set_reflections_pan(self,data):
        efx.alEffectf(self.effect, efx.AL_EAXREVERB_REFLECTIONS_PAN, data)
        self._reflections_pan = data

    def _get_reflections_pan(self):
        return self._reflections_pan

#min 0.0, max 10.0, default 1.26
    def _set_late_reverb_gain(self,data):
        efx.alEffectf(self.effect, efx.AL_EAXREVERB_LATE_REVERB_GAIN, data)
        self._late_reverb_gain = data

    def _get_late_reverb_gain(self):
        return self._late_reverb_gain

#min 0.0, max 0.1, default 0.011
    def _set_late_reverb_delay(self,data):
        efx.alEffectf(self.effect, efx.AL_EAXREVERB_LATE_REVERB_DELAY, data)
        self._late_reverb_delay = data

    def _get_late_reverb_delay(self):
        return self._late_reverb_delay

#default 0.0
    def _set_late_reverb_pan(self,data):
        efx.alEffectf(self.effect, efx.AL_EAXREVERB_LATE_REVERB_PAN, data)
        self._late_reverb_pan = data

    def _get_late_reverb_pan(self):
        return self._late_reverb_pan

#min 0.075, max 0.25, default 0.25
    def _set_echo_time(self,data):
        efx.alEffectf(self.effect, efx.AL_EAXREVERB_ECHO_TIME, data)
        self._echo_time = data

    def _get_echo_time(self):
        return self._echo_time

#min 0.0, max 1.0, default 0.0
    def _set_echo_depth(self,data):
        efx.alEffectf(self.effect, efx.AL_EAXREVERB_ECHO_DEPTH, data)
        self._echo_depth = data

    def _get_echo_depth(self):
        return self._echo_depth

#min 0.04, max 4.0, default 0.25
    def _set_modulation_time(self,data):
        efx.alEffectf(self.effect, efx.AL_EAXREVERB_MODULATION_TIME, data)
        self._modulation_time = data

    def _get_modulation_time(self):
        return self._modulation_time

#min 0.0, max 1.0, default 0.0
    def _set_modulation_depth(self,data):
        efx.alEffectf(self.effect, efx.AL_EAXREVERB_MODULATION_DEPTH, data)
        self._modulation_depth = data

    def _get_modulation_depth(self):
        return self._modulation_depth

#min 0.892, max 1.0, default 0.994
    def _set_air_absorption_gainhf(self,data):
        efx.alEffectf(self.effect, efx.AL_EAXREVERB_AIR_ABSORPTION_GAINHF, data)
        self._air_absorption_gainhf = data

    def _get_air_absorption_gainhf(self):
        return self._air_absorption_gainhf

#min 1000.0, ma 20000.0, default 5000.0
    def _set_hfreference(self,data):
        efx.alEffectf(self.effect, efx.AL_EAXREVERB_HFREFERENCE, data)
        self._hfreference = data

    def _get_hfreference(self):
        return self._hfreference

#min 20.0, max 1000.0, default 250.0
    def _set_lfreference(self,data):
        efx.alEffectf(self.effect, efx.AL_EAXREVERB_LFREFERENCE, data)
        self._lfreference = data

    def _get_lfreference(self):
        return self._lfreference

#min 0.0, max 10.0, default 0.0
    def _set_room_rolloff_factor(self,data):
        efx.alEffectf(self.effect, efx.AL_EAXREVERB_ROOM_ROLLOFF_FACTOR, data)
        self._room_rolloff_factor = data

    def _get_room_rolloff_factor(self):
        return self._room_rolloff_factor

#min AL_FALSE, max AL_TRUE, default AL_TRUE
    def _set_decay_hflimit(self,data):
        efx.alEffectf(self.effect, efx.AL_EAXREVERB_DECAY_HFLIMIT, data)
        self._decay_hflimit = data

    def _get_decay_hflimit(self):
        return self._decay_hflimit

#delete loaded sound
    def delete(self):
        al.alDeleteBuffers(1, self.effect)

    density = property(_get_density, _set_density, doc="""get/set density""")
    diffusion = property(_get_diffusion, _set_diffusion, doc="""get/set diffusion""")
    gain = property(_get_gain, _set_gain, doc="""get/set gain""")
    gainhf = property(_get_gainhf, _set_gainhf, doc="""get/set gainhf""")
    gainlf = property(_get_gainlf, _set_gainlf, doc="""get/set gainlf""")
    decay_time = property(_get_decay_time, _set_decay_time, doc="""get/set decay time""")
    decay_hfratio = property(_get_decay_hfratio, _set_decay_hfratio, doc="""get/set decay hfratio""")
    decay_lfratio = property(_get_decay_lfratio, _set_decay_lfratio, doc="""get/set decay lfratio""")
    reflections_gain = property(_get_reflections_gain, _set_reflections_gain, doc="""get/set reflections gain""")
    reflections_delay = property(_get_reflections_delay, _set_reflections_delay, doc="""get/set reflections delay""")
    reflections_pan = property(_get_reflections_pan, _set_reflections_pan, doc="""get/set reflections pan""")
    late_reverb_gain = property(_get_late_reverb_gain, _set_late_reverb_gain, doc="""get/set late reverb gain""")
    late_reverb_delay = property(_get_late_reverb_delay, _set_late_reverb_delay, doc="""get/set late reverb delay""")
    late_reverb_pan = property(_get_late_reverb_pan, _set_late_reverb_pan, doc="""get/set late reverb pan""")
    echo_time = property(_get_echo_time, _set_echo_time, doc="""get/set echo time""")
    echo_depth = property(_get_echo_depth, _set_echo_depth, doc="""get/set echo depth""")
    modulation_time = property(_get_modulation_time, _set_modulation_time, doc="""get/set modulation time""")
    modulation_depth = property(_get_modulation_depth, _set_modulation_depth, doc="""get/set modulation depth""")
    air_absorption_gainhf = property(_get_air_absorption_gainhf, _set_air_absorption_gainhf, doc="""get/set air absorption gainhf""")
    hfreference = property(_get_hfreference, _set_hfreference, doc="""get/set hfreference""")
    lfreference = property(_get_lfreference, _set_lfreference, doc="""get/set lfreference""")
    room_rolloff_factor = property(_get_room_rolloff_factor, _set_room_rolloff_factor, doc="""get/set room rolloff factor""")
    decay_hflimit = property(_get_decay_hflimit, _set_decay_hflimit, doc="""get/set decay hflimit""")






class chorus(object):
    def __init__(self):
    #log defaults
        self._waveform = 1
        self._phase =90
        self._rate = 1.1
        self._depth = 0.1
        self._feedback = 0.25
        self._delay = 0.016
    #allocate buffer
        self.effect = al.ALuint(0)

    #generate effect
        try:
            efx.alGenEffects(1,self.effect)
        except:
            print('ERROR: cant generate chorus effect')

    #set effect to echo
        efx.alEffecti(self.effect, efx.AL_EFFECT_TYPE, efx.AL_EFFECT_CHORUS)

#min 0 = Sinusoid, max 1 = Triangle, default 1
    def _set_waveform(self,data):
        efx.alEffectf(self.effect, efx.AL_CHORUS_WAVEFORM, data)
        self._waveform = data

    def _get_waveform(self):
        return self._waveform

#min -180, max 180, default 90
    def _set_phase(self,data):
        efx.alEffectf(self.effect, efx.AL_CHORUS_PHASE, data)
        self._phase = data

    def _get_phase(self):
        return self._phase

#min 0.0, max 10.0, default 1.1
    def _set_rate(self,data):
        efx.alEffectf(self.effect, efx.AL_CHORUS_RATE, data)
        self._rate = data

    def _get_rate(self):
        return self._rate

#min 0.0, max 1.0, default 0.1 
    def _set_depth(self,data):
        efx.alEffectf(self.effect, efx.AL_CHORUS_DEPTH, data)
        self._depth = data

    def _get_depth(self):
        return self._depth

#min -1.0, max 1.0, default 0.25
    def _set_feedback(self,data):
        efx.alEffectf(self.effect, efx.AL_CHORUS_FEEDBACK, data)
        self._feedback = data

    def _get_feedback(self):
        return self._feedback

#min 0.0, max 0.016, default 0.016
    def _set_delay(self,data):
        efx.alEffectf(self.effect, efx.AL_CHORUS_DELAY, data)
        self._delay = data

    def _get_delay(self):
        return self._delay

#delete loaded sound
    def delete(self):
        al.alDeleteBuffers(1, self.effect)

    waveform = property(_get_waveform, _set_waveform, doc="""get/set waveform""")
    phase = property(_get_phase, _set_phase, doc="""get/set phase""")
    rate = property(_get_rate, _set_rate, doc="""get/set rate""")
    depth = property(_get_depth, _set_depth, doc="""get/set depth""")
    feedback = property(_get_feedback, _set_feedback, doc="""get/set feedback""")
    delay = property(_get_delay, _set_delay, doc="""get/set delay""")
 




class distortion(object):
    def __init__(self):
    #log defaults
        self._distortion_edge = 0.2
        self._distortion_gain = 0.05
        self._distortion_lowpass_cutoff = 8000.0
        self._distortion_eqcenter = 3600.0
        self._distortion_eqbandwidth = 3600.0
    #allocate buffer
        self.effect = al.ALuint(0)

    #generate effect
        try:
            efx.alGenEffects(1,self.effect)
        except:
            print('ERROR: cant generate distorsion effect')

    #set effect to echo
        efx.alEffecti(self.effect, efx.AL_EFFECT_TYPE, efx.AL_EFFECT_DISTORTION)

#min 0.0, max 1.0, default 0.2
    def _set_distortion_edge(self,data):
        efx.alEffectf(self.effect, efx.AL_DISTORTION_EDGE, data)
        self._distortion_edge = data

    def _get_distortion_edge(self):
        return self._distortion_edge

#min 0.01, max 1.0, default 0.05
    def _set_distortion_gain(self,data):
        efx.alEffectf(self.effect, efx.AL_DISTORTION_GAIN, data)
        self._distortion_gain = data

    def _get_distortion_gain(self):
        return self._distortion_gain

#min 80.0, max 24000.0, default 8000.0
    def _set_distortion_lowpass_cutoff(self,data):
        efx.alEffectf(self.effect, efx.AL_DISTORTION_LOWPASS_CUTOFF, data)
        self._distortion_lowpass_cutoff = data

    def _get_distortion_lowpass_cutoff(self):
        return self._distortion_lowpass_cutoff

#min 80.0, max 24000.0, default 3600.0
    def _set_distortion_eqcenter(self,data):
        efx.alEffectf(self.effect, efx.AL_DISTORTION_EQCENTER, data)
        self._distortion_eqcenter = data

    def _get_distortion_eqcenter(self):
        return self._distortion_eqcenter

#min 80.0, max 24000.0, default 3600.0
    def _set_distortion_eqbandwidth(self,data):
        efx.alEffectf(self.effect, efx.AL_DISTORTION_EQBANDWIDTH, data)
        self._distortion_eqbandwidth = data

    def _get_distortion_eqbandwidth(self):
        return self._distortion_eqbandwidth

#delete loaded sound
    def delete(self):
        al.alDeleteBuffers(1, self.effect)

    distortion_edge = property(_get_distortion_edge, _set_distortion_edge, doc="""get/set distortion edge""")
    distortion_gain = property(_get_distortion_gain, _set_distortion_gain, doc="""get/set distortion gain""")
    distortion_lowpass_cutoff = property(_get_distortion_lowpass_cutoff, _set_distortion_lowpass_cutoff, doc="""get/set distortion lowpass cutoff""")
    distortion_eqcenter = property(_get_distortion_eqcenter, _set_distortion_eqcenter, doc="""get/set distortion eqcenter""")
    distortion_eqbandwidth = property(_get_distortion_eqbandwidth, _set_distortion_eqbandwidth, doc="""get/set distortion eqbandwidth""")






class echo(object):
    def __init__(self):
    #log defaults
        self._delay = 0.1
        self._LRdelay = 0.1
        self._damping = 0.5
        self._feedback = 0.5
        self._spread = -1.0
    #allocate buffer
        self.effect = al.ALuint(0)

    #generate effect
        try:
            efx.alGenEffects(1,self.effect)
        except:
            print('ERROR: cant generate echo effect')

    #set effect to echo
        efx.alEffecti(self.effect, efx.AL_EFFECT_TYPE, efx.AL_EFFECT_ECHO)

#min 0.0, max 0.207, default 0.1
    def _set_delay(self,data):
        efx.alEffectf(self.effect, efx.AL_ECHO_DELAY, data)
        self._delay = data

    def _get_delay(self):
        return self._delay

#min 0.0, max 0.404, default 0.1
    def _set_LRdelay(self,data):
        efx.alEffectf(self.effect, efx.AL_ECHO_LRDELAY, data)
        self._LRdelay = data

    def _get_LRdelay(self):
        return self._LRdelay

#min 0.0, max 0.99, default 0.5
    def _set_damping(self,data):
        efx.alEffectf(self.effect, efx.AL_ECHO_DAMPING, data)
        self._damping = data

    def _get_damping(self):
        return self._damping

#min 0.0, max 1.0, default 0.5
    def _set_feedback(self,data):
        efx.alEffectf(self.effect, efx.AL_ECHO_FEEDBACK, data)
        self._feedback = data

    def _get_feedback(self):
        return self._feedback

#min -1.0, max 1.0, default -1.0
    def _set_spread(self,data):
        efx.alEffectf(self.effect, efx.AL_ECHO_SPREAD, data)
        self._spread = data

    def _get_spread(self):
        return self._spread

#clean up resources
    def delete(self):
        efx.alDeleteEffects(1,self.effect)

    delay = property(_get_delay, _set_delay, doc="""get/set delay""")
    LRdelay = property(_get_LRdelay, _set_LRdelay, doc="""get/set left/right delay""")
    damping = property(_get_damping, _set_damping, doc="""get/set damping""")
    feedback = property(_get_feedback, _set_feedback, doc="""get/set feedback""")
    spread = property(_get_spread, _set_spread, doc="""get/set spread""")





class flanger(object):
    def __init__(self):
    #log defaults
        self._waveform = 1
        self._phase = 0
        self._rate = 0.27
        self._depth = 1.0
        self._feedback = -0.5
        self._delay = 0.002
    #allocate buffer
        self.effect = al.ALuint(0)

    #generate effect
        try:
            efx.alGenEffects(1,self.effect)
        except:
            print('ERROR: cant generate flanger effect')

    #set effect to echo
        efx.alEffecti(self.effect, efx.AL_EFFECT_TYPE, efx.AL_EFFECT_FLANGER)

#min 0, max 1, default 1
    def _set_waveform(self,data):
        efx.alEffectf(self.effect, efx.AL_FLANGER_WAVEFORM, data)
        self._waveform = data

    def _get_waveform(self):
        return self._waveform

#min -180, max 180, default 0
    def _set_phase(self,data):
        efx.alEffectf(self.effect, efx.AL_FLANGER_PHASE, data)
        self._phase = data

    def _get_phase(self):
        return self._phase

#min 0.0, max 10.0, default 0.27
    def _set_rate(self,data):
        efx.alEffectf(self.effect, efx.AL_FLANGER_RATE, data)
        self._rate = data

    def _get_rate(self):
        return self._rate

#min 0.0, max 1.0, default 1.0
    def _set_depth(self,data):
        efx.alEffectf(self.effect, efx.AL_FLANGER_DEPTH, data)
        self._depth = data

    def _get_depth(self):
        return self._depth

#min -1.0, max 1.0, default -0.5
    def _set_feedback(self,data):
        efx.alEffectf(self.effect, efx.AL_FLANGER_FEEDBACK, data)
        self._feedback = data

    def _get_feedback(self):
        return self._feedback

#min 0.0, max 0.004, default 0.002
    def _set_delay(self,data):
        efx.alEffectf(self.effect, efx.AL_FLANGER_DELAY, data)
        self._delay = data

    def _get_delay(self):
        return self._delay

#delete loaded sound
    def delete(self):
        al.alDeleteBuffers(1, self.effect)

    waveform = property(_get_waveform, _set_waveform, doc="""get/set waveform""")
    phase = property(_get_phase, _set_phase, doc="""get/set phase""")
    rate = property(_get_rate, _set_rate, doc="""get/set rate""")
    depth = property(_get_depth, _set_depth, doc="""get/set depth""")
    feedback = property(_get_feedback, _set_feedback, doc="""get/set feedback""")
    delay = property(_get_delay, _set_delay, doc="""get/set delay""")




class frequency_shifter(object):
    def __init__(self):
    #log defaults
        self._shifter_frequency = 0.0
        self._shifter_left_direction = 0
        self._shifter_right_direction = 0
    #allocate buffer
        self.effect = al.ALuint(0)

    #generate effect
        try:
            efx.alGenEffects(1,self.effect)
        except:
            print('ERROR: cant generate frequency shifter effect')

    #set effect to echo
        efx.alEffecti(self.effect, efx.AL_EFFECT_TYPE, efx.AL_EFFECT_FREQUENCY_SHIFTER)

#min 0.0, max 24000.0, default 0.0
    def _set_shifter_frequency(self,data):
        efx.alEffectf(self.effect, efx.AL_FREQUENCY_SHIFTER_FREQUENCY, data)
        self._shifter_frequency = data

    def _get_shifter_frequency(self):
        return self._shifter_frequency

#min 0, max 2, default 0
    def _set_shifter_left_direction(self,data):
        efx.alEffectf(self.effect, efx.AL_FREQUENCY_SHIFTER_LEFT_DIRECTION, data)
        self._shifter_left_direction = data

    def _get_shifter_left_direction(self):
        return self._shifter_left_direction

#min 0, max 2, default 0
    def _set_shifter_right_direction(self,data):
        efx.alEffectf(self.effect, efx.AL_FREQUENCY_SHIFTER_RIGHT_DIRECTION, data)
        self._shifter_right_direction = data

    def _get_shifter_right_direction(self):
        return self._shiter_right_direction

#delete loaded sound
    def delete(self):
        al.alDeleteBuffers(1, self.effect)

    shifter_frequency = property(_get_shifter_frequency, _set_shifter_frequency, doc="""get/set shifter frequency""")
    shifter_left_direction = property(_get_shifter_left_direction, _set_shifter_left_direction, doc="""get/set shifter left direction""")
    shifter_right_direction = property(_get_shifter_right_direction, _set_shifter_right_direction, doc="""get/set shifter right direction""")




class vocal_morpher(object):
    def __init__(self):
    #log defaults
        self._phonemea = 0
        self._phonemea_coarse_tuning = 0
        self._phonemeb = 10
        self._phonemeb_coarse_tuning = 0
        self._waveform = 0
        self._rate = 1.41
    #allocate buffer
        self.effect = al.ALuint(0)

    #generate effect
        try:
            efx.alGenEffects(1,self.effect)
        except:
            print('ERROR: cant generate vocal morpher effect')

    #set effect to echo
        efx.alEffecti(self.effect, efx.AL_EFFECT_TYPE, efx.AL_EFFECT_VOCAL_MORPHER)

#min 0, max 29, default 0
    def _set_phonemea(self,data):
        efx.alEffectf(self.effect, efx.AL_VOCAL_MORPHER_PHONEMEA, data)
        self._phonemea = data

    def _get_phonemea(self):
        return self._phonemea

#min -24, max 24, default 0
    def _set_phonemea_coarse_tuning(self,data):
        efx.alEffectf(self.effect, efx.AL_VOCAL_MORPHER_PHONEMEA_COARSE_TUNING, data)
        self._phonemea_coarse_tuning = data

    def _get_phonemea_coarse_tuning(self):
        return self._phonemea_coarse_tuning

#min 0, max 29, default 10
    def _set_phonemeb(self,data):
        efx.alEffectf(self.effect, efx.AL_VOCAL_MORPHER_PHONEMEB, data)
        self._phonemeb = data

    def _get_phonemeb(self):
        return self._phonemeb

#min -24, max 24, default 0
    def _set_phonemeb_coarse_tuning(self,data):
        efx.alEffectf(self.effect, efx.AL_VOCAL_MORPHER_PHONEMEB_COARSE_TUNING, data)
        self._phonemeb_coarse_tuning = data

    def _get_phonemeb_coarse_tuning(self):
        return self._phonemeb_coarse_tuning

#min 0, max 2, default 0
    def _set_waveform(self,data):
        efx.alEffectf(self.effect, efx.AL_VOCAL_MORPHER_WAVEFORM, data)
        self._waveform = data

    def _get_waveform(self):
        return self._waveform
        
#min 0.0, max 10.0, default 1.41
    def _set_rate(self,data):
        efx.alEffectf(self.effect, efx.AL_VOCAL_MORPHER_RATE, data)
        self._rate = data

    def _get_rate(self):
        return self._rate

#delete loaded sound
    def delete(self):
        al.alDeleteBuffers(1, self.effect)

    phonemea = property(_get_phonemea, _set_phonemea, doc="""get/set phonemea""")
    phonemea_coarse_tuning = property(_get_phonemea_coarse_tuning, _set_phonemea_coarse_tuning, doc="""get/set phonemea coarse tuning""")
    phonemeb = property(_get_phonemeb, _set_phonemeb, doc="""get/set phonemeb""")
    phonemeb_coarse_tuning = property(_get_phonemeb_coarse_tuning, _set_phonemeb_coarse_tuning, doc="""get/set phonemeb coarse tuning""")
    waveform = property(_get_waveform, _set_waveform, doc="""get/set waveform""")
    rate = property(_get_rate, _set_rate, doc="""get/set rate""")




class pitch_shifter(object):
    def __init__(self):
    #log defaults
        self._coarse_tune = 12
        self._fine_tune = 0
    #allocate buffer
        self.effect = al.ALuint(0)

    #generate effect
        try:
            efx.alGenEffects(1,self.effect)
        except:
            print('ERROR: cant generate pitch shifter effect')

    #set effect to echo
        efx.alEffecti(self.effect, efx.AL_EFFECT_TYPE, efx.AL_EFFECT_PITCH_SHIFTER)

#min -12, max 12, default 12
    def _set_coarse_tune(self,data):
        efx.alEffectf(self.effect, efx.AL_PITCH_SHIFTER_COARSE_TUNE, data)
        self._coarse_tune = data

    def _get_coarse_tune(self):
        return self._coarse_tune

#min -50, max 50, default 0
    def _set_fine_tune(self,data):
        efx.alEffectf(self.effect, efx.AL_PITCH_SHIFTER_FINE_TUNE, data)
        self._fine_tune = data

    def _get_fine_tune(self):
        return self._fine_tune

#delete loaded sound
    def delete(self):
        al.alDeleteBuffers(1, self.effect)

    coarse_tune = property(_get_coarse_tune, _set_coarse_tune, doc="""get/set coarse tune""")
    fine_tune = property(_get_fine_tune, _set_fine_tune, doc="""get/set fine tune""")





class ring_modulator(object):
    def __init__(self):
    #log defaults
        self._frequency = 440.0
        self._highpass_cutoff = 800.0
        self._waveform = 0
    #allocate buffer
        self.effect = al.ALuint(0)

    #generate effect
        try:
            efx.alGenEffects(1,self.effect)
        except:
            print('ERROR: cant generate ring modulator effect')

    #set effect to echo
        efx.alEffecti(self.effect, efx.AL_EFFECT_TYPE, efx.AL_EFFECT_RING_MODULATOR)

#min 0.0, max 8000.0, default 440.0
    def _set_frequency(self,data):
        efx.alEffectf(self.effect, efx.AL_RING_MODULATOR_FREQUENCY, data)
        self._frequency = data

    def _get_frequency(self):
        return self._frequency

#min 0.0, max 24000.0, default 800.0
    def _set_highpass_cutoff(self,data):
        efx.alEffectf(self.effect, efx.AL_RING_MODULATOR_HIGHPASS_CUTOFF, data)
        self._highpass_cutoff = data

    def _get_highpass_cutoff(self):
        return self._highpass_cutoff

#min 0, max 2, default 0
    def _set_waveform(self,data):
        efx.alEffectf(self.effect, efx.AL_RING_MODULATOR_WAVEFORM, data)
        self._waveform = data

    def _get_waveform(self):
        return self._waveform

#delete loaded sound
    def delete(self):
        al.alDeleteBuffers(1, self.effect)

    frequency = property(_get_frequency, _set_frequency, doc="""get/set frequency""")
    highpass_cutoff = property(_get_highpass_cutoff, _set_highpass_cutoff, doc="""get/set highpass cutoff""")
    waveform = property(_get_waveform, _set_waveform, doc="""get/set waveform""")
    
    




class autowah(object):
    def __init__(self):
    #log defaults
        self._attack_time = 0.06
        self._release_time = 0.06
        self._resonance = 1000.0
        self._peak_gain = 11.22
    #allocate buffer
        self.effect = al.ALuint(0)

    #generate effect
        try:
            efx.alGenEffects(1,self.effect)
        except:
            print('ERROR: cant generate autowah effect')

    #set effect to echo
        efx.alEffecti(self.effect, efx.AL_EFFECT_TYPE, efx.AL_EFFECT_AUTOWAH)

#min 0.0001, max 1.0, default 0.06
    def _set_attack_time(self,data):
        efx.alEffectf(self.effect, efx.AL_AUTOWAH_ATTACK_TIME, data)
        self._attack_time = data

    def _get_attack_time(self):
        return self._attack_time

#min 0.0001, max 1.0, default 0.06
    def _set_release_time(self,data):
        efx.alEffectf(self.effect, efx.AL_AUTOWAH_RELEASE_TIME, data)
        self._release_time = data

    def _get_release_time(self):
        return self._release_time

#min 2.0, max 1000.0, default 1000.0
    def _set_resonance(self,data):
        efx.alEffectf(self.effect, efx.AL_AUTOWAH_RESONANCE, data)
        self._resonance = data

    def _get_resonance(self):
        return self._resonance

#min 0.00003, max 31621.0, default 11.22
    def _set_peak_gain(self,data):
        efx.alEffectf(self.effect, efx.AL_AUTOWAH_PEAK_GAIN, data)
        self._peak_gain = data

    def _get_peak_gain(self):
        return self._peak_gain

#delete loaded sound
    def delete(self):
        al.alDeleteBuffers(1, self.effect)

    attack_time = property(_get_attack_time, _set_attack_time, doc="""get/set attack time""")
    release_time = property(_get_release_time, _set_release_time, doc="""get/set release time""")
    resonance = property(_get_resonance, _set_resonance, doc="""get/set resonance""")
    peak_gain = property(_get_peak_gain, _set_peak_gain, doc="""get/set peak gain""")
    




class compressor(object):
    def __init__(self):
        self._active = True
    #allocate buffer
        self.effect = al.ALuint(0)

    #generate effect
        try:
            efx.alGenEffects(1,self.effect)
        except:
            print('ERROR: cant generate compressor effect')

    #set effect to echo
        efx.alEffecti(self.effect, efx.AL_EFFECT_TYPE, efx.AL_EFFECT_COMPRESSOR)

    def _set_on_off(self,data):
        if data == True and self._active == False:
            efx.alEffectf(self.effect, efx.AL_COMPRESSOR_ONOFF, al.AL_TRUE)
            self._active = True
        elif data == False and self._active == True:
            efx.alEffectf(self.effect, efx.AL_COMPRESSOR_ONOFF, al.AL_FALSE)
            self._active = False

    def _get_on_off(self):
        return self._active

#delete loaded sound
    def delete(self):
        al.alDeleteBuffers(1, self.effect)

    on_off = property(_get_on_off, _set_on_off, doc="""turn compressor on/off""")



class equalizer(object):
    def __init__(self):
    #log defaults
        self._low_gain = 1.0
        self._low_cutoff = 200.0
        self._mid1_gain = 1.0
        self._mid1_center = 500.0
        self._mid1_width = 1.0
        self._mid2_gain = 1.0
        self._mid2_center = 3000.0
        self._mid2_width = 1.0
        self._high_gain = 1.0
        self._high_cutoff = 6000.0
    #allocate buffer
        self.effect = al.ALuint(0)

    #generate effect
        try:
            efx.alGenEffects(1,self.effect)
        except:
            print('ERROR: cant generate equalizer effect')

    #set effect to echo
        efx.alEffecti(self.effect, efx.AL_EFFECT_TYPE, efx.AL_EFFECT_EQUALIZER)

#min 0.126, max 7.943, default 1.0
    def _set_low_gain(self,data):
        efx.alEffectf(self.effect, efx.AL_EQUALIZER_LOW_GAIN, al.AL_FALSE)
        self._low_gain = data

    def _get_low_gain(self):
        return self._low_gain

#min 50.0, max 800.0, default 200.0
    def _set_low_cutoff(self,data):
        efx.alEffectf(self.effect, efx.AL_EQUALIZER_LOW_CUTOFF, al.AL_FALSE)
        self._low_cutoff = data

    def _get_low_cutoff(self):
        return self._low_cutoff

#min 0.126, max 7.943, default 1.0
    def _set_mid1_gain(self,data):
        efx.alEffectf(self.effect, efx.AL_EQUALIZER_MID1_GAIN, al.AL_FALSE)
        self._mid1_gain = data

    def _get_mid1_gain(self):
        return self._mid1_gain

#min 200.0, max 3000.0, default 500.0
    def _set_mid1_center(self,data):
        efx.alEffectf(self.effect, efx.AL_EQUALIZER_MID1_CENTER, al.AL_FALSE)
        self._mid1_center = data

    def _get_mid1_center(self):
        return self._mid1_center

#min 0.01, max 1..0, default 1.0
    def _set_mid1_width(self,data):
        efx.alEffectf(self.effect, efx.AL_EQUALIZER_MID1_WIDTH, al.AL_FALSE)
        self._mid1_width = data

    def _get_mid1_width(self):
        return self._mid1_width

#min 0.126, max 7.943, default 1.0
    def _set_mid2_gain(self,data):
        efx.alEffectf(self.effect, efx.AL_EQUALIZER_MID2_GAIN, al.AL_FALSE)
        self._mid2_gain = data

    def _get_mid2_gain(self):
        return self._mid2_gain

#min 1000.0, max 8000.0, default 3000.0
    def _set_mid2_center(self,data):
        efx.alEffectf(self.effect, efx.AL_EQUALIZER_MID2_CENTER, al.AL_FALSE)
        self._mid2_center = data

    def _get_mid2_center(self):
        return self._mid2_center

#min 0.01, max 1.0, default 1.0
    def _set_mid2_width(self,data):
        efx.alEffectf(self.effect, efx.AL_EQUALIZER_MID2_WIDTH, al.AL_FALSE)
        self._mid2_width = data

    def _get_mid2_width(self):
        return self._mid2_width

#min 0.126, max 7.943, default 1.0
    def _set_high_gain(self,data):
        efx.alEffectf(self.effect, efx.AL_EQUALIZER_HIGH_GAIN, al.AL_FALSE)
        self._high_gain = data

    def _get_high_gain(self):
        return self._high_gain

#min 4000.0, max 16000.0, default 6000.0
    def _set_high_cutoff(self,data):
        efx.alEffectf(self.effect, efx.AL_EQUALIZER_HIGH_CUTOFF, al.AL_FALSE)
        self._high_cutoff = data

    def _get_high_cutoff(self):
        return self._high_cutoff

#delete loaded sound
    def delete(self):
        al.alDeleteBuffers(1, self.effect)

    low_gain = property(_get_low_gain, _set_low_gain, doc="""get/set low gain""")
    low_cutoff = property(_get_low_cutoff, _set_low_cutoff, doc="""get/set low cutoff""")
    mid1_gain = property(_get_mid1_gain, _set_mid1_gain, doc="""get/set mid1 gain""")
    mid1_center = property(_get_mid1_center, _set_mid1_center, doc="""get/set mid1 center""")
    mid1_width = property(_get_mid1_width, _set_mid1_width, doc="""get/set mid1 width""")
    mid2_gain = property(_get_mid2_gain, _set_mid2_gain, doc="""get/set mid2 gain""")
    mid2_center = property(_get_mid2_center, _set_mid2_center, doc="""get/set mid2 center""")
    mid2_width = property(_get_mid2_width, _set_mid2_width, doc="""get/set mid2 width""")
    high_gain = property(_get_high_gain, _set_high_gain, doc="""get/set high gain""")
    high_cutoff = property(_get_high_cutoff, _set_high_cutoff, doc="""get/set high cutoff""")




class lowpass_filter(object):
    def __init__(self):
    #log defaults
        self._gain = 1.0
        self._gainlf = 1.0

    #allocate buffer
        self.filter = al.ALuint(0)

    #generate filter
        try:
            efx.alGenFilters(1,self.filter)
        except:
            print('ERROR: cant generate lowpass filter')

    #set to lowpass filter
        efx.alFilteri(self.filter, efx.AL_FILTER_TYPE, efx.AL_FILTER_LOWPASS)

#min 0.0, max 1.0, default 1.0
    def _set_gain(self,data):
        efx.alFilterf(self.filter, efx.AL_HIGHPASS_GAIN, data)
        self._gain = data

    def _get_gain(self):
        return self._gain

#min 0.0, max 1.0, default 1.0
    def _set_gainlf(self,data):
        efx.alFilterf(self.filter, efx.AL_HIGHPASS_GAINLF, data)
        self._gainlf = data

    def _get_gainlf(self):
        return self._gainlf

    def delete(self):
        efx.alDeleteFilters(1,self.filter)

    gain = property(_get_gain, _set_gain, doc="""get/set gain""")
    gainlf = property(_get_gainlf, _set_gainlf, doc="""get/set gainlf""")





class highpass_filter(object):
    def __init__(self):
    #log defaults
        self._gain = 1.0
        self._gainlf = 1.0
        
    #allocate buffer
        self.filter = al.ALuint(0)

    #generate effect
        try:
            efx.alGenFilters(1,self.filter)
        except:
            print('ERROR: cant generate highpass filter')

    #set effect to echo
        efx.alFilteri(self.filter, efx.AL_FILTER_TYPE, efx.AL_FILTER_HIGHPASS)

#min 0.0, max 1.0, default 1.0
    def _set_gain(self,data):
        efx.alFilterf(self.filter, efx.AL_HIGHPASS_GAIN, data)
        self._gain = data

    def _get_gain(self):
        return self._gain

#min 0.0, max 1.0, default 1.0
    def _set_gainlf(self,data):
        efx.alFilterf(self.filter, efx.AL_HIGHPASS_GAINLF, data)
        self._gainlf = data

    def _get_gainlf(self):
        return self._gainlf

    def delete(self):
        efx.alDeleteFilters(1,self.filter)

    gain = property(_get_gain, _set_gain, doc="""get/set gain""")
    gainlf = property(_get_gainlf, _set_gainlf, doc="""get/set gainlf""")





class bandpass_filter(object):
    def __init__(self):
    #log defaults
        self._gain = 1.0
        self._gainlf = 1.0
        self._gainhf = 1.0

    #allocate buffer
        self.filter = al.ALuint(0)

    #generate effect
        try:
            efx.alGenFilters(1,self.filter)
        except:
            print('ERROR: cant generate bandpass filter')

    #set effect to echo
        efx.alFilteri(self.filter, efx.AL_FILTER_TYPE, efx.AL_FILTER_BANDPASS)

#min 0.0, max 1.0, default 1.0
    def _set_gain(self,data):
        efx.alFilterf(self.filter, efx.AL_BANDPASS_GAIN,data)
        self._gain = data

    def _get_gain(self):
        return self._gain

#min 0.0, max 1.0, default 1.0
    def _set_gainlf(self,data):
        efx.alFilterf(self.filter, efx.AL_BANDPASS_GAINLF, data)
        self._gainlf = data

    def _get_gainlf(self):
        return self._gainlf

#min 0.0, max 1.0, default 1.0
    def _set_gainhf(self,data):
        efx.alFilterf(self.filter, efx.AL_BANDPASS_GAINHF, data)
        self._gainhf = data

    def _get_gainhf(self):
        return self._gainhf

#min 0.0, max 1.0, default 1.0
    def delete(self):
        efx.alDeleteFilters(1,self.filter)

    gain = property(_get_gain, _set_gain, doc="""get/set gain""")
    gainlf = property(_get_gainlf, _set_gainlf, doc="""get/set gainlf""")
    gainhf = property(_get_gainhf, _set_gainhf, doc="""get/set gainhf""")
    




Example()
