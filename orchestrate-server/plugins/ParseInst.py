"""
    This plugin is used to update the MIDI file with the new instrument specified by the user.
"""
class ParseInst():
    def __init__(self, inst_map):
        """
            Constructor for ParseInst class.
        """
        self.inst_map = inst_map


    def change_instrument(self, midi_file, new_instrument):
        """
            Load the midi file and change the instrument
            Inputs:
                midi_file: path to the midi file
                new_instrument: new instrument to be used
            Outputs:
                midi_file: midi file with the new instrument
        """
        for i in range(len(midi_file.instruments)):
            midi_file.instruments[i].program = self.inst_map[new_instrument]
        return midi_file

