"""
    Module to Generate Chords based on the input
"""
import numpy as np


def chord_selector(key: str, key_chords_dict: dict) -> list:
    """
        Select a chord based on the key
        Input:
            key {str} : Key of the song
            chord_dict {dict} : Dictionary of key/chords
        Output:
            key_chords_list {list} : List of chords
    """
    # randomly select a number from 0-4
    random_num = np.random.randint(0, 4)

    # select a chord based on the key
    # randomly select a chord from the list
    # lower 
    chord_list = key_chords_dict[key]
    key_chords_list = chord_list[random_num]

    return key_chords_list



def generate_chords(chords: list, num_measures: int, time_signature: str) -> str:
    """
        Generate chords based on the input
        Input:
            chords {list} : Chord list extracted from NLP prompt
            num_measures {int} : Number of measures extracted from NLP prompt
            time_signature {str} : Time signature extracted from NLP prompt
        Output:
            chord_progression {str} : formatted chord progression
    """
    # extract time signature numerator divided by 2
    numerator = int(time_signature.split("/")[0])
    denominator = int(time_signature.split("/")[1])
    num_notes_per_measures = numerator / denominator * 8
    # num_notes_per_half_measures = num_notes_per_measures//2
    # chord_repeats = int(time_signature.split("/")[0]) * 2

    # add chords
    while len(chords) < num_measures:
        chords.extend(chords)

    # if the chord overextends the number of measures, trim the chord list
    if len(chords) > num_measures:
        chords = chords[:num_measures]

    # iterate through the chord list and repeat each chord with
    # 1. number of measures
    # 2. number of chord repeats
    chord_progression_list = []
    for chord in chords:
        chord_progression_list.extend([chord] * int(num_notes_per_measures))

    # chord_progression_list = chord_progression_list * int(num_measures//4) 
    # print(chord_progression_list)

    # join by hyphen and renove white spaces
    chord_progression = "-".join(chord_progression_list)
    chord_progression = chord_progression.replace(" ", "")
    return chord_progression



if __name__ == "__main__":
    chords = ['C', 'A', 'B'] #+ ['C', 'A', 'B'] + ['C', 'A'] 
    num_measures = 8
    time_signature = '3/4'
    chord_progression = generate_chords(chords, num_measures, time_signature)


