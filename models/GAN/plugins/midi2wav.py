"""
    Class to Convert MIDI files to WAV files
"""
import glob
from midi2audio import FluidSynth

class midi2wav():
    def __init__(self):
        """Class Constructor to convert midi files to wav files"""
        pass


    def convert(self, midi_path, output_path):
        """
            Convert a single midi file to wav
            Input:
                - midi_path: path to the midi file
                - output_path: path to save the wav file
        """
        fs = FluidSynth()
        fs.midi_to_audio(midi_path, output_path)


