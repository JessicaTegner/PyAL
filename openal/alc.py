import ctypes
from . import dll

__all__ = ["ALC_FALSE", "ALC_TRUE", "ALC_INVALID", "ALC_FREQUENCY",
           "ALC_REFRESH", "ALC_SYNC", "ALC_MONO_SOURCES", "ALC_STEREO_SOURCES",
           "ALC_NO_ERROR", "ALC_INVALID_DEVICE", "ALC_INVALID_CONTEXT",
           "ALC_INVALID_ENUM", "ALC_INVALID_VALUE", "ALC_OUT_OF_MEMORY",
           "ALC_DEFAULT_DEVICE_SPECIFIER", "ALC_DEVICE_SPECIFIER",
           "ALC_EXTENSIONS", "ALC_MAJOR_VERSION", "ALC_MINOR_VERSION",
           "ALC_ATTRIBUTES_SIZE", "ALC_ALL_ATTRIBUTES",
           "ALC_DEFAULT_ALL_DEVICES_SPECIFIER", "ALC_ALL_DEVICES_SPECIFIER",
           "ALC_CAPTURE_DEVICE_SPECIFIER",
           "ALC_CAPTURE_DEFAULT_DEVICE_SPECIFIER", "ALC_CAPTURE_SAMPLES",
           "ALC_HRTF_SOFT", "ALC_HRTF_ID_SOFT", "ALC_DONT_CARE_SOFT",
           "ALC_HRTF_STATUS_SOFT", "ALC_NUM_HRTF_SPECIFIERS_SOFT",
           "ALC_HRTF_SPECIFIER_SOFT", "ALC_HRTF_DISABLED_SOFT",
           "ALC_HRTF_ENABLED_SOFT", "ALC_HRTF_DENIED_SOFT",
           "ALC_HRTF_REQUIRED_SOFT", "ALC_HRTF_HEADPHONES_DETECTED_SOFT",
           "ALC_HRTF_UNSUPPORTED_FORMAT_SOFT",
           "ALCboolean", "ALCchar", "ALCbyte", "ALCubyte", "ALCshort",
           "ALCushort", "ALCint", "ALCuint", "ALCsizei", "ALCenum", "ALCfloat",
           "ALCdouble", "ALCvoid", "ALCdevice", "ALCcontext",
           "alcCreateContext", "alcMakeContextCurrent", "alcProcessContext",
           "alcSuspendContext", "alcDestroyContext", "alcGetCurrentContext",
           "alcGetContextsDevice", "alcOpenDevice", "alcCloseDevice",
           "alcGetError", "alcIsExtensionPresent", "alcGetProcAddress",
           "alcGetEnumValue", "alcGetString", "alcGetIntegerv",
           "alcCaptureOpenDevice", "alcCaptureCloseDevice", "alcCaptureStart",
           "alcCaptureStop", "alcCaptureSamples", "alcGetStringiSOFT",
           "alcResetDeviceSOFT",
           ]

_bind = dll.bind_function

ALC_INVALID = 0
ALC_FALSE = 0
ALC_TRUE = 1

ALC_FREQUENCY = 0x1007
ALC_REFRESH = 0x1008
ALC_SYNC = 0x1009

ALC_MONO_SOURCES = 0x1010
ALC_STEREO_SOURCES = 0x1011

ALC_NO_ERROR = ALC_FALSE
ALC_INVALID_DEVICE = 0xA001
ALC_INVALID_CONTEXT = 0xA002
ALC_INVALID_ENUM = 0xA003
ALC_INVALID_VALUE = 0xA004
ALC_OUT_OF_MEMORY = 0xA005

ALC_DEFAULT_DEVICE_SPECIFIER = 0x1004
ALC_DEVICE_SPECIFIER = 0x1005
ALC_EXTENSIONS = 0x1006

ALC_MAJOR_VERSION = 0x1000
ALC_MINOR_VERSION = 0x1001

ALC_ATTRIBUTES_SIZE = 0x1002
ALC_ALL_ATTRIBUTES = 0x1003

ALC_DEFAULT_ALL_DEVICES_SPECIFIER = 0x1012
ALC_ALL_DEVICES_SPECIFIER = 0x1013

ALC_CAPTURE_DEVICE_SPECIFIER = 0x310
ALC_CAPTURE_DEFAULT_DEVICE_SPECIFIER = 0x311
ALC_CAPTURE_SAMPLES = 0x312

ALC_HRTF_SOFT = 0x1992
ALC_HRTF_ID_SOFT = 0x1996
ALC_DONT_CARE_SOFT = 0x002
ALC_HRTF_STATUS_SOFT = 0x1993
ALC_NUM_HRTF_SPECIFIERS_SOFT = 0x1994
ALC_HRTF_SPECIFIER_SOFT = 0x1995
ALC_HRTF_DISABLED_SOFT = 0x0000
ALC_HRTF_ENABLED_SOFT = 0x0001
ALC_HRTF_DENIED_SOFT = 0x0002
ALC_HRTF_REQUIRED_SOFT = 0x0003
ALC_HRTF_HEADPHONES_DETECTED_SOFT = 0x0004
ALC_HRTF_UNSUPPORTED_FORMAT_SOFT = 0x0005

ALCboolean = ctypes.c_char
ALCchar = ctypes.c_char
ALCbyte = ctypes.c_char
ALCubyte = ctypes.c_ubyte
ALCshort = ctypes.c_short
ALCushort = ctypes.c_ushort
ALCint = ctypes.c_int
ALCuint = ctypes.c_uint
ALCsizei = ctypes.c_int
ALCenum = ctypes.c_int
ALCfloat = ctypes.c_float
ALCdouble = ctypes.c_double
ALCvoid = None


class ALCdevice(ctypes.Structure):
    """A OpenAL device used for audio operations."""
    pass


class ALCcontext(ctypes.Structure):
    """An execution context on a OpenAL device."""
    pass

alcCreateContext = _bind("alcCreateContext", [ctypes.POINTER(ALCdevice),
                                              ctypes.POINTER(ALCint)],
                         ctypes.POINTER(ALCcontext))
alcMakeContextCurrent = _bind("alcMakeContextCurrent",
                              [ctypes.POINTER(ALCcontext)], ALCboolean)
alcProcessContext = _bind("alcProcessContext", [ctypes.POINTER(ALCcontext)])
alcSuspendContext = _bind("alcSuspendContext", [ctypes.POINTER(ALCcontext)])
alcDestroyContext = _bind("alcDestroyContext", [ctypes.POINTER(ALCcontext)])
alcGetCurrentContext = _bind("alcGetCurrentContext", None,
                             ctypes.POINTER(ALCcontext))
alcGetContextsDevice = _bind("alcGetContextsDevice",
                             [ctypes.POINTER(ALCcontext)],
                             ctypes.POINTER(ALCdevice))
alcOpenDevice = _bind("alcOpenDevice", [ctypes.POINTER(ALCchar)],
                      ctypes.POINTER(ALCdevice))
alcCloseDevice = _bind("alcCloseDevice", [ctypes.POINTER(ALCdevice)],
                       ALCboolean)
alcGetError = _bind("alcGetError", [ctypes.POINTER(ALCdevice)], ALCenum)
alcIsExtensionPresent = _bind("alcIsExtensionPresent",
                              [ctypes.POINTER(ALCdevice),
                               ctypes.POINTER(ALCchar)])
alcGetProcAddress = _bind("alcGetProcAddress", [ctypes.POINTER(ALCdevice),
                                                ctypes.POINTER(ALCchar)],
                          ctypes.c_void_p)
alcGetEnumValue = _bind("alcGetEnumValue", [ctypes.POINTER(ALCdevice),
                                            ctypes.POINTER(ALCchar)], ALCenum)
alcGetString = _bind("alcGetString", [ctypes.POINTER(ALCdevice), ALCenum],
                     ctypes.POINTER(ALCchar))
alcGetIntegerv = _bind("alcGetIntegerv", [ctypes.POINTER(ALCdevice),
                                          ALCenum, ALCsizei,
                                          ctypes.POINTER(ALCint)])
alcCaptureOpenDevice = _bind("alcCaptureOpenDevice",
                             [ctypes.POINTER(ALCchar), ALCuint, ALCenum,
                              ALCsizei], ctypes.POINTER(ALCdevice))
alcCaptureCloseDevice = _bind("alcCaptureCloseDevice",
                              [ctypes.POINTER(ALCdevice)])
alcCaptureStart = _bind("alcCaptureStart", [ctypes.POINTER(ALCdevice)])
alcCaptureStop = _bind("alcCaptureStop", [ctypes.POINTER(ALCdevice)])
alcCaptureSamples = _bind("alcCaptureSamples", [ctypes.POINTER(ALCdevice),
                                                ctypes.POINTER(ALCvoid),
                                                ALCsizei])

alcGetStringiSOFT = _bind("alcGetStringiSOFT", [ctypes.POINTER(ALCdevice),
                                                  ctypes.POINTER(ALCenum),
                                                  ctypes.POINTER(ALCsizei)])
alcResetDeviceSOFT = _bind("alcResetDeviceSOFT", [ctypes.POINTER(ALCdevice),
                                                  ctypes.POINTER(ALCint)])
