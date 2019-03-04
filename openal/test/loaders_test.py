import os
import sys
import unittest
from .. import al, loaders

RESPATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources")


class OpenALAudioTest(unittest.TestCase):

    def test_load_file(self):
        wavfile = os.path.join(RESPATH, "hey.wav")
        snddata = loaders.load_file(wavfile)

        self.assertEqual(snddata.format, al.AL_FORMAT_MONO16)
        self.assertEqual(snddata.frequency, 44100)
        self.assertEqual(snddata.size, 122880)

    def test_load_wav_file(self):
        wavfile = os.path.join(RESPATH, "hey.wav")
        snddata = loaders.load_wav_file(wavfile)

        self.assertEqual(snddata.format, al.AL_FORMAT_MONO16)
        self.assertEqual(snddata.frequency, 44100)
        self.assertEqual(snddata.size, 122880)

    @unittest.skip("not implemented")
    def test_load_stream(self):
        pass


if __name__ == "__main__":
    sys.exit(unittest.main())
