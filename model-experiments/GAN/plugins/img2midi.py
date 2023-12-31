"""
    Class to convert midi piano roll images back to MIDI files
    Enable playable file format for the generated images
"""
import numpy as np
from PIL import Image
from music21 import instrument, note, chord, stream

class img2midi():
    def __init__(self, image_path, output_path, resolution = 0.25, lowerBoundNote = 21):
        """
            Class Constructor to convert midi piano roll images back to MIDI files
            Input:
                - image_path: path to the image
                - output_path: path to save the MIDI file
                - resolution: resolution of the image, each pixel represents resolution quarter notes
                - lowerBoundNote: lowest note to be considered
        """
        self.image_path = image_path
        self.output_path = output_path
        self.resolution = resolution
        self.lowerBoundNote = lowerBoundNote

    
    def column2notes(self, column):
        """
            Convert a column to a list of notes
            Since 255 was use to denote a note, 
            if the value of the pixel is greater than 255/2 threshole it is considered a note
            Input:
                - column: column of the image
            Output:
                - list of notes
        """
        notes = []
        for i in range(len(column)):
            if column[i] > 255/2:
                notes.append(i+self.lowerBoundNote)
        return notes
    

    def updateNotes(self, newNotes, prevNotes):
        """
            Update the dictionary of notes
            For each pixel that made up a note scale it by the resolution
            Input:
                - newNotes: new notes to be added
                - prevNotes: previous notes
            Output:
                - updated dictionary of notes
        """
        res = {} 
        for note in newNotes:
            if note in prevNotes:
                res[note] = prevNotes[note] + self.resolution
            else:
                res[note] = self.resolution
        return res
    

    def convert_to_midi(self, name):
        """
            Convert the image to notes and create a midi file from the notes
        """

        # Open the Image and convert it to a numpy array
        with Image.open(self.image_path) as image:
            im_arr = np.frombuffer(image.tobytes(), dtype=np.uint8)
            try:
                im_arr = im_arr.reshape((image.size[1], image.size[0]))
            except:
                im_arr = im_arr.reshape((image.size[1], image.size[0],3))
                im_arr = np.dot(im_arr, [0.33, 0.33, 0.33])

        offset = 0
        output_notes = []


        # create note and chord objects based on the values generated by the model
        prev_notes = self.updateNotes(im_arr.T[0,:], {})
        for column in im_arr.T[1:,:]:
            notes = self.column2notes(column)
            # pattern is a chord
            notes_in_chord = notes
            old_notes = prev_notes.keys()
            for old_note in old_notes:
                if not old_note in notes_in_chord:
                    new_note = note.Note(old_note,quarterLength=prev_notes[old_note])
                    new_note.storedInstrument = instrument.Piano()
                    if offset - prev_notes[old_note] >= 0:
                        new_note.offset = offset - prev_notes[old_note]
                        output_notes.append(new_note)
                    elif offset == 0:
                        new_note.offset = offset
                        output_notes.append(new_note)                    
                    else:
                        print(offset,prev_notes[old_note],old_note)

            prev_notes = self.updateNotes(notes_in_chord,prev_notes)

            # increase offset each iteration so that notes do not stack
            offset += self.resolution

        for old_note in prev_notes.keys():
            new_note = note.Note(old_note,quarterLength=prev_notes[old_note])
            new_note.storedInstrument = instrument.Piano()
            new_note.offset = offset - prev_notes[old_note]

            output_notes.append(new_note)

        # TODO: streamline naming
        prev_notes = self.updateNotes(notes_in_chord,prev_notes)
        midi_stream = stream.Stream(output_notes)
        midi_stream.write('midi', fp=f"{self.output_path}/{name}")
