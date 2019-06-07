"""Utility classes for OpenAL-based audio access."""
from collections.abc import Iterable
import ctypes
import os
from . import al, alc


__all__ = ["SoundListener", "SoundSource", "SoundData", "SoundSink",
           "OpenALError",
           ]


# Helper functions
_to_ctypes = lambda seq, dtype: (len(seq) * dtype)(*seq)
_to_python = lambda seq: [x.value for x in seq]


# Error handling
_ERRMAP = {al.AL_NO_ERROR: "No Error",
           al.AL_INVALID_NAME: "Invalid name",
           al.AL_INVALID_ENUM: "Invalid enum",
           al.AL_INVALID_VALUE: "Invalid value",
           al.AL_INVALID_OPERATION: "Invalid operation",
           al.AL_OUT_OF_MEMORY: "Out of memory",
           alc.ALC_NO_ERROR: "No Error",
           alc.ALC_INVALID_DEVICE: "Invalid device",
           alc.ALC_INVALID_CONTEXT: "Invalid context",
           alc.ALC_INVALID_ENUM: "Invalid ALC enum",
           alc.ALC_INVALID_VALUE: "Invalid ALC value",
           alc.ALC_OUT_OF_MEMORY: "Out of memory"
           }
_get_error_message = lambda x: _ERRMAP.get(x, "Error code [%d]" % x)


def _continue_or_raise(alcdevice=None):
    """Raises an OpenALError, if an error flag is set."""
    if alcdevice:
        err = alc.alcGetError(alcdevice)
        if err != alc.ALC_NO_ERROR:
            raise OpenALError(_get_error_message(err))
    else:
        err = al.alGetError()
        if err != al.AL_NO_ERROR:
            raise OpenALError(_get_error_message(err))


# Property update handling on SoundListener, SoundData and SoundSource
_SOURCEPROPMAP = {
    "pitch": al.AL_PITCH,
    "gain": al.AL_GAIN,
    "max_distance": al.AL_MAX_DISTANCE,
    "rolloff_factor": al.AL_ROLLOFF_FACTOR,
    "reference_distance": al.AL_REFERENCE_DISTANCE,
    "min_gain": al.AL_MIN_GAIN,
    "max_gain": al.AL_MAX_GAIN,
    "cone_outer_gain": al.AL_CONE_OUTER_GAIN,
    "cone_inner_angle": al.AL_CONE_INNER_ANGLE,
    "cone_outer_angle": al.AL_CONE_OUTER_ANGLE,
    "position": al.AL_POSITION,
    "velocity": al.AL_VELOCITY,
    "direction": al.AL_DIRECTION,
    "source_relative": al.AL_SOURCE_RELATIVE,
    "source_type": al.AL_SOURCE_TYPE,
    "looping": al.AL_LOOPING,
    "buffer": al.AL_BUFFER,
    "source_state": al.AL_SOURCE_STATE,
    "sec_offset": al.AL_SEC_OFFSET,
    "sample_offset": al.AL_SAMPLE_OFFSET,
    "byte_offset": al.AL_BYTE_OFFSET,
    "buffers_queued": al.AL_BUFFERS_QUEUED,
    "buffers_processed": al.AL_BUFFERS_PROCESSED,
    }

_LISTENERPROPMAP = {
    # Listener properties
    "orientation": al.AL_ORIENTATION,
    "position": al.AL_POSITION,
    "velocity": al.AL_VELOCITY,
    "gain": al.AL_GAIN,
    }

_BUFFERPROPMAP = {
    # Buffer properties
    "frequency": al.AL_FREQUENCY,
    "bits": al.AL_BITS,
    "channels": al.AL_CHANNELS,
    "size": al.AL_SIZE,
    }

_CTXPROPMAP = {
    # Context Manager properties
    "frequency": alc.ALC_FREQUENCY,
    "mono_sources": alc.ALC_MONO_SOURCES,
    "stereo_sources": alc.ALC_STEREO_SOURCES,
    "refresh": alc.ALC_REFRESH,
    "sync": alc.ALC_SYNC,
    }

# The callbacks are
# ([elemcount, ]type setter, getter)
#
# For buffers in OpenAL 1.1 all props are specified as read-only, hence
# the SoundData structure ignores those information, but stores
# everything in properties, without interacting with OpenAL.
#
_BUFFERCALLBACKS = {
        al.AL_FREQUENCY: (al.ALint, al.alBufferi, al.alGetBufferi),
        al.AL_BITS: (al.ALint, al.alBufferi, al.alGetBufferi),
        al.AL_CHANNELS: (al.ALint, al.alBufferi, al.alGetBufferi),
        al.AL_SIZE: (al.ALint, al.alBufferi, al.alGetBufferi),
        }
def _get_buffer_value(bufid, prop):
    """Gets the requested OpenAL buffer property value."""
    _Type, setter, getter = _BUFFERCALLBACKS[prop]
    v = _Type()
    getter(bufid, prop, v)
    return v
def _set_buffer_value(bufid, prop, value):
    """Sets a OpenAL buffer property value."""
    _BUFFERCALLBACKS[prop][1](bufid, prop, value)


def add_buffer_extension(propname, proptype, valuetype, getter, setter):
    """Binds a OpenAL buffer extension to all newly created SoundData/buffer
    instances. Returns True, if the AL buffer extension is supported, False
    otherwise."""
    propname = propname.upper()
    if propname.startswith("al.AL_"):
        pname = propname[3:]
    else:
        pname = propname
        propname = "al.AL_%s" % propname
    if al.alIsExtensionPresent(pname) == al.AL_FALSE:
        return False

    global _BUFFERCALLBACKS
    global _BUFFERPROPMAP
    _BUFFERCALLBACKS[proptype] = (valuetype, getter, setter)
    _BUFFERPROPMAP[propname] = proptype
    return True

_LISTENERCALLBACKS = {
        al.AL_GAIN: (1, al.ALfloat, al.alListenerf, al.alListenerf),
        al.AL_POSITION: (3, al.ALfloat, al.alListenerfv, al.alGetListenerfv),
        al.AL_VELOCITY: (3, al.ALfloat, al.alListenerfv, al.alGetListenerfv),
        al.AL_ORIENTATION: (6, al.ALfloat, al.alListenerfv, al.alGetListenerfv),
        }
def _get_listener_value(prop):
    """Gets the requested OpenAL listener property value."""
    size, _Type, setter, getter = _LISTENERCALLBACKS[prop]
    v = (_Type * size)()
    getter(prop, v)
    return v
def _set_listener_value(prop, value):
    """Sets a OpenAL listener property value."""
    size, _Type, setter, getter = _LISTENERCALLBACKS[prop]
    if size > 1:
        value = _to_ctypes(value, _Type)
    setter(prop, value)


def add_listener_extension(propname, proptype, vcount, valuetype, getter,
                           setter):
    """Binds a OpenAL listener extension to all newly created SoundListener
    instances. Returns True, if the listener extension is supported, False
    otherwise."""
    propname = propname.upper()
    if propname.startswith("al.AL_"):
        pname = propname[3:]
    else:
        pname = propname
        propname = "al.AL_%s" % propname
    if al.alIsExtensionPresent(pname) == al.AL_FALSE:
        return False

    global _LISTENERCALLBACKS
    global _LISTENERPROPMAP
    _LISTENERCALLBACKS[proptype] = (vcount, valuetype, getter, setter)
    _LISTENERPROPMAP[propname] = proptype
    return True


_SOURCECALLBACKS = {
        al.AL_PITCH: (1, al.ALfloat, al.alSourcef, al.alGetSourcef),
        al.AL_GAIN: (1, al.ALfloat, al.alSourcef, al.alGetSourcef),
        al.AL_MAX_DISTANCE: (1, al.ALfloat, al.alSourcef, al.alGetSourcef),
        al.AL_ROLLOFF_FACTOR: (1, al.ALfloat, al.alSourcef, al.alGetSourcef),
        al.AL_REFERENCE_DISTANCE: (1, al.ALfloat, al.alSourcef, al.alGetSourcef),
        al.AL_MIN_GAIN: (1, al.ALfloat, al.alSourcef, al.alGetSourcef),
        al.AL_MAX_GAIN: (1, al.ALfloat, al.alSourcef, al.alGetSourcef),
        al.AL_CONE_OUTER_GAIN: (1, al.ALfloat, al.alSourcef, al.alGetSourcef),
        al.AL_CONE_INNER_ANGLE: (1, al.ALfloat, al.alSourcef, al.alGetSourcef),
        al.AL_CONE_OUTER_ANGLE: (1, al.ALfloat, al.alSourcef, al.alGetSourcef),
        al.AL_POSITION: (3, al.ALfloat, al.alSourcefv, al.alGetSourcefv),
        al.AL_VELOCITY: (3, al.ALfloat, al.alSourcefv, al.alGetSourcefv),
        al.AL_DIRECTION: (3, al.ALfloat, al.alSourcefv, al.alGetSourcefv),
        al.AL_SOURCE_RELATIVE: (1, al.ALint, al.alSourcei, al.alGetSourcei),
        al.AL_SOURCE_TYPE: (1, al.ALint, al.alSourcei, al.alGetSourcei),
        al.AL_LOOPING: (1, al.ALint, al.alSourcei, al.alGetSourcei),
        al.AL_SOURCE_STATE: (1, al.ALint, al.alSourcei, al.alGetSourcei),
        al.AL_BUFFERS_QUEUED: (1, al.ALint, None, al.alGetSourcei),
        al.AL_BUFFERS_PROCESSED: (1, al.ALint, None, al.alGetSourcei),
        al.AL_SEC_OFFSET: (1, al.ALfloat, al.alSourcef, al.alGetSourcef),
        al.AL_SAMPLE_OFFSET: (1, al.ALfloat, al.alSourcef, al.alGetSourcef),
        al.AL_BYTE_OFFSET: (1, al.ALfloat, al.alSourcef, al.alGetSourcef),
        }
def _get_source_value(sourceid, prop):
    """Gets the requested OpenAL source property value."""
    size, _Type, setter, getter = _SOURCECALLBACKS[prop]
    v = (_Type * size)()
    getter(sourceid, prop, v)
    return v
def _set_source_value(sourceid, prop, value):
    """Sets a OpenAL source property value."""
    size, _Type, setter, getter = _SOURCECALLBACKS[prop]
    if size > 1:
        value = _to_ctypes(value, _Type)
    setter(sourceid, prop, value)


def add_source_extension(propname, proptype, vcount, valuetype, getter, setter):
    """Binds a OpenAL source extension to all newly created SoundSource
    instances. Returns True, if the AL source extension is supported, False
    otherwise."""
    propname = propname.upper()
    if propname.startswith("al.AL_"):
        pname = propname[3:]
    else:
        pname = propname
        propname = "al.AL_%s" % propname
    if al.alIsExtensionPresent(pname) == al.AL_FALSE:
        return False

    global _SOURCECALLBACKS
    global _SOURCEPROPMAP
    _SOURCECALLBACKS[proptype] = (vcount, valuetype, getter, setter)
    _SOURCEPROPMAP[propname] = proptype
    return True


class OpenALError(Exception):
    """An OpenAL specific exception class."""
    def __init__(self, msg=None, alcdevice=None):
        """Creates a new OpenALError instance with the specified message.

        If no msg is provided, the message will be set a mapped value of
        alGetError(). If an ALCdevice is provided as alcdevice, alcGetError()
        will be used instead of alGetError().
        """
        super(OpenALError, self).__init__()
        self.msg = msg
        self.errcode = -1
        if msg is None:
            if alcdevice:
                self.errcode = alc.alcGetError(alcdevice)
                self.msg = _get_error_message(self.errcode)
            else:
                self.errcode = al.alGetError()
                self.msg = _get_error_message(self.errcode)

    def __str__(self):
        return repr(self.msg)


class SoundData(object):
    """A buffered audio object.

    The SoundData consists of a PCM audio data buffer, the audio frequency
    and additional format information to allow easy buffering through OpenAL.
    """
    def __init__(self, data=None, channels=None, bitrate=None, size=None,
                 frequency=None, dformat=None):
        """Creates a new SoundData object."""
        self.channels = channels
        self.bitrate = bitrate
        self.size = size
        self.frequency = frequency
        self.data = data
        if dformat is None:
            formatmap = {(1, 8): al.AL_FORMAT_MONO8,
                         (2, 8): al.AL_FORMAT_STEREO8,
                         (1, 16): al.AL_FORMAT_MONO16,
                         (2, 16): al.AL_FORMAT_STEREO16
                         }
            dformat = formatmap.get((channels, bitrate), None)
        self.format = dformat


class StreamingSoundData(SoundData):
    """A streaming audio object.

    The StreamingSoundData consists of a PCM audio stream, the audio frequency
    and format information. It reads and fills a buffer automatically on
    underruns.
    """
    def __init__(self, stream=None, channels=None, bitrate=None, size=None,
                 frequency=None):
        """Creates a new StreamingSoundData object."""
        super(StreamingSoundData, self).__init__(stream, channels, bitrate,
                                                 size, frequency)
        self.streaming = True

    def read(self, size=None):
        return self.data.read(size)

    def seek(self, offset, whence=os.SEEK_SET):
        self.data.seek(offset, whence)

    def tell(self):
        return self.data.tell()


class SoundListener(object):
    """A listener object within the 3D audio space."""
    def __init__(self, position=[0, 0, 0], velocity=[0, 0, 0],
                 orientation=[0, 0, -1, 0, 1, 0]):
        """Creates a new SoundListener with a specific position, movement
        velocity and hearing orientation."""
        self.dataproperties = {}
        self.dataproperties[al.AL_POSITION] = position
        self.dataproperties[al.AL_VELOCITY] = velocity
        self.dataproperties[al.AL_ORIENTATION] = orientation
        self.changedproperties = [al.AL_POSITION, al.AL_VELOCITY,
                                  al.AL_ORIENTATION]

    def __getattr__(self, name):
        if name in ("dataproperties", "changedproperties"):
            return super(SoundListener, self).__getattr__(name)
        dprop = _LISTENERPROPMAP.get(name, None)
        if dprop is None:
            raise AttributeError("object %r has no attribute %r" % \
                                     (self.__class__.__name__, name))
        # Either get the value or return None, if it has not been
        # fetched yet.
        return self.dataproperties.get(dprop, None)

    def __setattr__(self, name, value):
        if name in ("dataproperties", "changedproperties"):
            return super(SoundListener, self).__setattr__(name, value)
        dprop = _LISTENERPROPMAP.get(name, None)
        if dprop is None:
            raise AttributeError("object %r has no attribute %r" % \
                                     (self.__class__.__name__, name))
        self.dataproperties[dprop] = value
        if dprop not in self.changedproperties:
            self.changedproperties.append(dprop)

    def __delattr__(self, name):
        if name in ("dataproperties", "changedproperties"):
            return super(SoundListener, self).__delattr__(name)
        dprop = _LISTENERPROPMAP.get(name, None)
        if dprop is None:
            raise AttributeError("object %r has no attribute %r" % \
                                     (self.__class__.__name__, name))
        self.dataproperties.pop(dprop, None)

    @property
    def changed(self):
        """Indicates, if one or more properties changed since the last
        update."""
        return len(self.changedproperties) != 0


class SoundSource(object):
    """An object within the application world, which can emit sounds."""
    def __init__(self, gain=1.0, pitch=1.0, position=[0, 0, 0],
                 velocity=[0, 0, 0]):
        self.bufferqueue = []
        self.dataproperties = {}
        self.dataproperties[al.AL_GAIN] = gain
        self.dataproperties[al.AL_PITCH] = pitch
        self.dataproperties[al.AL_POSITION] = position
        self.dataproperties[al.AL_VELOCITY] = velocity
        self.changedproperties = [al.AL_GAIN, al.AL_PITCH, al.AL_POSITION,
                                  al.AL_VELOCITY]

    def __getattr__(self, name):
        if name in ("dataproperties", "changedproperties", "bufferqueue"):
            return super(SoundSource, self).__getattr__(name)
        dprop = _SOURCEPROPMAP.get(name, None)
        if dprop is None:
            raise AttributeError("object %r has no attribute %r" % \
                                     (self.__class__.__name__, name))
        # Either get the value or return None, if it has not been
        # fetched yet.
        return self.dataproperties.get(dprop, None)

    def __setattr__(self, name, value):
        if name in ("dataproperties", "changedproperties", "bufferqueue"):
            return super(SoundSource, self).__setattr__(name, value)
        dprop = _SOURCEPROPMAP.get(name, None)
        if dprop is None:
            raise AttributeError("object %r has no attribute %r" % \
                                     (self.__class__.__name__, name))
        self.dataproperties[dprop] = value
        if dprop not in self.changedproperties:
            self.changedproperties.append(dprop)

    def __delattr__(self, name):
        if name in ("dataproperties", "changedproperties", "bufferqueue"):
            return super(SoundSource, self).__delattr__(name)
        dprop = _SOURCEPROPMAP.get(name, None)
        if dprop is None:
            raise AttributeError("object %r has no attribute %r" % \
                                     (self.__class__.__name__, name))
        self.dataproperties.pop(dprop, None)

    @property
    def changed(self):
        """Indicates, that one or more properties changed since the last
        update."""
        return len(self.changedproperties) != 0

    def queue(self, sounddata):
        """Adds a SoundData object for playback to the SoundSource."""
        self.bufferqueue.append(sounddata)


class SoundSink(object):
    """Audio playback system.

    The SoundSink handles audio output for sound sources. It connects to an
    audio output device and manages the source settings, buffer queues and
    the playback of them.
    """
    MAX_BUFFERS_PER_SOURCE = 10
    MAX_BUFFER_SIZE = 48000

    def __init__(self, device=None, attributes=None):
        """Creates a new SoundSink for a specific audio output device."""
        if isinstance(device, alc.ALCdevice):
            self.device = device
            self._deviceopened = False
        else:
            self._deviceopened = True
            device = alc.alcOpenDevice(device)
            if not device:
                raise OpenALError(alc=True)
            self.device = device.contents
        if attributes:
            attributes = _to_ctypes(attributes, alc.ALCint)
        context = alc.alcCreateContext(device, attributes)
        if not context:
            raise OpenALError(alc=True)
        self.context = context.contents

        self._sources = {}
        self._sids = {}
        self._streams = {}
        self._listener = None

    def __del__(self):
        context = getattr(self, "context", None)
        if context:
            alc.alcDestroyContext(context)
        self.context = None
        if self._deviceopened:
            alc.alcCloseDevice(self.device)
        self.device = None

    def activate(self):
        """Marks the SoundSink as being the current one for operating on
        the OpenAL states."""
        alc.alcMakeContextCurrent(self.context)
        _continue_or_raise(self.device)

    @property
    def listener(self):
        """Gets or sets the SoundListener of the SoundSink."""
        if self._listener is None:
            self._listener = SoundListener()
        return self._listener

    @listener.setter
    def listener(self, value):
        """Gets or sets the SoundListener of the SoundSink."""
        self._listener = value

    @property
    def opened_device(self):
        """Gets, whether the SoundSink initially opened the device."""
        return self._deviceopened

    def refresh(self, source):
        """Refreshes the passed SoundSource's internal state."""
        sid = self._sources.get(source, None)
        if sid is None:
            raise ValueError("source not associated with the SoundSink")
        for key in _SOURCECALLBACKS:
            source.dataproperties[key] = _to_python(_get_source_value(sid, key))

    def _create_source_id(self, source):
        """Creates a OpenAL source id for the passed SoundSource."""
        if source in self._sources:
            # We should have a OpenAL source id already
            return self._sources[source]
        # None yet, create a new one or bind it to an existing id
        sid = None
        for p, v in self._sids.items():
            if v is None:
                # Unused sid, use that one
                sid = p
        if not sid:
            sid = al.ALuint()
            al.alGenSources(1, sid)
            _continue_or_raise()
        self._sources[source] = sid.value
        self._sids[sid.value] = source
        return sid.value

    def play(self, sources):
        """Starts playing the buffered sounds of the source or sources."""
        if isinstance(sources, Iterable):
            sids = []
            for source in sources:
                sid = self._create_source_id(source)
                sids.append(sid)
            al.alSourcePlayv(_to_ctypes(sids, al.ALuint), len(sids))
        else:
            sid = self._create_source_id(sources)
            al.alSourcePlay(sid)
        _continue_or_raise()

    def stop(self, sources):
        """Stops playing the buffered sounds of the source or sources."""
        if isinstance(sources, Iterable):
            sids = [self._sources[source] for source in sources
                    if source in self._sources]
            al.alSourceStopv(_to_ctypes(sids, al.ALuint), len(sids))
        elif sources in self._sources:
            al.alSourceStop(self._sources[sources])
        _continue_or_raise()

    def pause(self, sources):
        """Pauses the playback of the buffered sounds of the source or
        sources."""
        if isinstance(sources, Iterable):
            sids = [self._sources[source] for source in sources
                    if source in self._sources]
            al.alSourcePausev(_to_ctypes(sids, al.ALuint), len(sids))
        elif sources in self._sources:
            al.alSourcePause(self._sources[sources])
        _continue_or_raise()

    def rewind(self, sources):
        """Rewinds the buffers of the source or sources."""
        if isinstance(sources, Iterable):
            sids = [self._sources[source] for source in sources
                    if source in self._sources]
            al.alSourceRewindv(_to_ctypes(sids, al.ALuint), len(sids))
        elif sources in self._sources:
            al.alSourceRewind(self._sources[sources])
        _continue_or_raise()

    def process_source(self, source):
        """Processes the passed SoundSource."""
        sid = self._create_source_id(source)
        # Apply the changed information of the source, if any
        props = getattr(source, "changedproperties", [])
        for prop in props:
            _set_source_value(sid, prop, source.dataproperties[prop])
        source.changedproperties = []

        # Check the OpenAL buffers for the sid
        bufcount = al.ALint()
        freebufs = []
        al.alGetSourcei(sid, al.AL_BUFFERS_PROCESSED, ctypes.byref(bufcount))
        bufcount = bufcount.value
        while bufcount > 0:
            bufid = al.ALuint()
            al.alSourceUnqueueBuffers(sid, 1, ctypes.byref(bufid))
            freebufs.append(bufid)
            bufcount -= 1

        queued = al.ALint()
        al.alGetSourcei(sid, al.AL_BUFFERS_QUEUED, ctypes.byref(queued))
        _continue_or_raise()
        queued = queued.value

        # Check the source's buffer queue
        while queued < self.MAX_BUFFERS_PER_SOURCE:
            if len(source.bufferqueue) == 0:
                break
            data = source.bufferqueue.pop(0)
            if len(freebufs) > 0:
                bufid = freebufs.pop()
            else:
                bufid = al.ALuint()
                al.alGenBuffers(1, ctypes.byref(bufid))
                _continue_or_raise()

            if getattr(data, "streaming", False):
                # A stream that has to be read into a ring buffer
                sids = self._streams.get(data, {})
                offset, size = sids.get(sid)
                bufsize = min(self.MAX_BUFFER_SIZE, size - offset)
                bufdata = data.read(bufsize)
                source.bufferqueue.insert(data)
            else:
                # A simple sound object - do not stream it.
                bufdata = data.data
                bufsize = data.size
            # Queue the complete data.
            state = al.ALint()
            al.alGetSourcei(sid, al.AL_SOURCE_STATE, ctypes.byref(state))
            if state not in (al.AL_PAUSED, al.AL_PLAYING):
                al.alBufferData(bufid, data.format, bufdata, bufsize,
                                data.frequency)
                _continue_or_raise()
                al.alSourceQueueBuffers(sid, 1, bufid)
                _continue_or_raise()
                al.alSourcePlay(sid)
            queued += 1

    def process_listener(self):
        """Processes the SoundListener attached to the SoundSink."""
        props = getattr(self.listener, "changedproperties", [])
        for prop in props:
            _set_listener_value(prop, self.listener.dataproperties[prop])
        self.listener.changedproperties = []

    def update(self):
        """Processes all currently attached sound sources."""
        self.process_listener()
        process_source = self.process_source
        for source in self._sources:
            process_source(source)
