"""
    Class to convert midi files to images
    Each note can be represented as a block, 
    the height of the block is defines by the pitch of the note
    the width of the block is defined by the duration of the note
"""
import sys
import numpy as np
from music21 import converter, instrument, note, chord
from imageio import imwrite

class midi2img():
    def __init__(self, 
                 output_path="./",
                 max_repetitions = float("inf"), 
                 resolution = 0.25, 
                 lowerBoundNote = 21, 
                 upperBoundNote = 127, 
                 maxSongLength = 100):
        """
            Class Constructor to convert midi files to images
            Input:
                - midi_path: path to the midi file
                - output_path: path to save the images
                - max_repetitions: maximum number of repetitions of the song,
                    if the song is shorter than maxSongLength*max_repetitions, 
                    the song will be padded with zeros
                - resolution: resolution of the image, each pixel represents resolution quarter notes
                - lowerBoundNote: lowest note to be considered
                - upperBoundNote: highest note to be considered
                - maxSongLength: maximum number of quarter notes per image
        """
        self.output_path = output_path
        self.max_repetitions = max_repetitions
        self.resolution = resolution
        self.lowerBoundNote = lowerBoundNote
        self.upperBoundNote = upperBoundNote
        self.maxSongLength = maxSongLength


    def extractPitch(self, element):
        """
            Extract the pitch of a note or chord
            Input:
                - element: element of the MIDI file
            Output:
                - pitch of the note
        """
        return int(element.pitch.ps)
    

    def extractDuration(self, element):
        """
            Extract the duration of a note or chord
            Input:
                - element: element of the MIDI file
            Output:
                - duration of the note
        """
        return element.duration.quarterLength
    

    def parseMIDI(self, notes_to_parse):
        """
            Get all the notes and chords from a given midi file content
            Input:
                - notes_to_parse: notes of the MIDI file
            Output:
                - dictionary with the start time, pitch and duration of each note
        """
        labels = []
        durations = []
        notes = []
        start = []


        for element in notes_to_parse:
            # For each element in the content of the MIDI file, ignoring rests
            # Check if it is a note or a chord
            # If it is a note, extract the pitch and duration
            # If it is a chord, extract the pitch and duration of each note in the chord
            if isinstance(element, note.Note):
                if element.isRest:
                    continue
                labels.append(str(element.name))
                start.append(element.offset)
                notes.append(self.extractPitch(element))
                durations.append(self.extractDuration(element))

                    
            elif isinstance(element, chord.Chord):
                if element.isRest:
                    continue
                for chord_note in element:
                    labels.append(str(element.commonName))
                    start.append(element.offset)
                    durations.append(self.extractDuration(element))
                    notes.append(self.extractPitch(chord_note))
        return {"labels": labels, "start":start, "pitch":notes,  "dur":durations}



    def convert_to_image(self, midi_path):
        """
            Convert the MIDI file to an image
            Output:
                - dictionary with the name of the instrument and the corresponding image
        """
        data = {}

        # Read the MIDI file, and separate the instruments
        mid = converter.parse(midi_path)
        instruments = instrument.partitionByInstrument(mid)
            
        # data extraction
        try:
            i=0
            # For each instrument, 
            # get a dictionary of the start, pitch, and duration of each note using get_notes()
            # save the note data by instrument
            for instrument_i in instruments.parts:
                notes_to_parse = instrument_i.recurse()
                notes_data = self.parseMIDI(notes_to_parse)
                if len(notes_data["start"]) == 0:
                    continue

                # If the instrument has no name, name it "instrument_i"
                # If the instrument has a name, name it "instrument_i.partName"
                if instrument_i.partName is None:
                    data["instrument_{}".format(i)] = notes_data
                    i+=1
                else:
                    data[instrument_i.partName] = notes_data

        except:
            # if the midi file has a flat structure (one instrument or no instrument)
            # get a dictionary of the start, pitch, and duration of each note using get_notes() for structure
            notes_to_parse = mid.flat.notes
            data["instrument_0"] = self.parseMIDI(notes_to_parse)


        # data processing 
        # for each instrument, align the notes in a matrix
        # the matrix has shape (upperBoundNote-lowerBoundNote, maxSongLength)
        # each element of the matrix (pixel) represents resolution quarter notes
        # maxSongLength is the maximum number of quarter notes per image, represnted by the width of the image
        # (upperBoundNote-lowerBoundNote) is the maximum number of notes that can be played at the same time, represented by the height of the image
        img_data = {}

        for instrument_name, values in data.items():
            # The pitch of the note is represented by the height of the block
            # The duration of the note is represented by the width of the block
            # https://en.wikipedia.org/wiki/Scientific_pitch_notation#Similar_systems
            pitches = values["pitch"]
            durs = values["dur"]
            starts = values["start"]

            # Define a separate matrix for each repetition of the song
            index = 0
            while index < self.max_repetitions:
                
                matrix = np.zeros((self.upperBoundNote-self.lowerBoundNote, self.maxSongLength))

                # For each note, add a block to the matrix
                # Scale the duration and start time of the note by the defined resolution of the image
                for dur, start, pitch in zip(durs, starts, pitches):
                    dur = int(dur/self.resolution)
                    start = int(start/self.resolution)


                    # If the note is out of bounds, ignore it
                    # If the note is in bounds, add a block to the matrix by setting the corresponding pixels to 255
                    if not start > index*(self.maxSongLength+1) or not dur+start < index*self.maxSongLength:
                        for j in range(start, start+dur):
                            if j - index*self.maxSongLength >= 0 and j - index*self.maxSongLength < self.maxSongLength:
                                matrix[pitch-self.lowerBoundNote,j - index*self.maxSongLength] = 255

                # add the corresponding matrix to the dictionary
                img_data[f"{instrument_name}_{index}"] = matrix

                # If matrix contains no notes (only zeros) don't save it
                image_name = midi_path.split("/")[-1].replace(".mid",f"_{instrument_name}_{index}.png")
                if matrix.any(): 
                    imwrite(f"{self.output_path}/{image_name}", matrix.astype(np.uint8))
                    index += 1
                else:
                    break

        return img_data, data



if __name__ == "__main__":
    midi_path = "../../data/piano/0fithos.mid"
    output_path = "../../data/midi_imag"
    midi2img_obj = midi2img(midi_path, output_path, max_repetitions = 1)
    img, data = midi2img_obj.convert_to_image()
    print(data)