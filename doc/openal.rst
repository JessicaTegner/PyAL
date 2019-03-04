.. module:: openal
   :synopsis: Simple OpenAL wrapper module

Direct OpenAL interaction
=========================
:mod:`openal` is a simple (really, really simple) wrapper around the bindings
offered by the OpenAL 1.1 specification. Each constant, type and function
defined by the standard can be found within :mod:`openal`. There are no
additional object structures, safety nets or whatever else, so that you can
transfer code written using :mod:`openal` easily to any other platform in a 1:1
manner.

.. highlight:: c

A brief example in C code::

    #include <AL/al.h>
    #include <AL/alc.h>
  
    int main(int argc, char *argv[]) {
        ALuint source;
        ALCdevice *device;
        ALCcontext *context;
       
        device = alcOpenDevice(NULL);
        if (device == NULL)
        {
            ALenum error = alcGetError();
            /* do something with the error */
            return -1;
        }
        /* Omit error checking */
        context = alcCreateContext(device, NULL);
        alcMakeContextCurrent(context);
        
        /* Do more things */
        alGenSources(1, &source);
        alSourcef(source, AL_PITCH, 1);
        alSourcef(source, AL_GAIN, 1);
        alSource3f(source, AL_POSITION, 10, 0, 0);
        alSource3f(source, AL_VELOCITY, 0, 0, 0);
        alSourcei(source, AL_LOOPING, 1);
        
        alDeleteSources(1, &source);
        alcDestroyContext(context);
        alcCloseDevice(device);
        return 0;
    }

.. highlight:: python

Doing the same in Python: ::

    from openal import al, alc    # imports all relevant AL and ALC functions
    
    def main():
        source = al.ALuint()
        device = alc.alcOpenDevice(None)
        if not device:
            error = alc.alcGetError()
            # do something with the error, which is a ctypes value
            return -1
        # Omit error checking
        context = alc.alcCreateContext(device, None)
        alc.alcMakeContextCurrent(context)

        # Do more things
        al.alGenSources(1, source)
        al.alSourcef(source, al.AL_PITCH, 1)
        al.alSourcef(source, al.AL_GAIN, 1)
        al.alSource3f(source, al.AL_POSITION, 10, 0, 0)
        al.alSource3f(source, al.AL_VELOCITY, 0, 0, 0)
        al.alSourcei(source, al.AL_LOOPING, 1)
        
        al.alDeleteSources(1, source)
        alc.alcDestroyContext(context)
        alc.alcCloseDevice(device)
        return 0

    if __name__ == "__main__":
        raise SystemExit(main())
    

This does not feel very pythonic, does it? As initially said, :mod:`openal` is a
really simple, really thin wrapper around the OpenAL functions. If you want a
more advanced access to 3D positional audio, you might want to read on about
:mod:`openal.audio`.
