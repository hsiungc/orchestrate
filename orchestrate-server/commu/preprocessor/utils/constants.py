import enum
from typing import List, Optional

class KeySwitchVelocity(int, enum.Enum):
    DEFAULT = 1

    @classmethod
    def get_value(cls, key: Optional[str]) -> int:
        key = key or "DEFAULT"
        if hasattr(cls, key):
            return getattr(cls, key).value
        return cls.DEFAULT.value

class ChordType(str, enum.Enum):
    MAJOR = "major"
    MINOR = "minor"

    @classmethod
    def values(cls) -> List[str]:
        return list(cls.__members__.values())

BPM_INTERVAL = 5
CHORD_TRACK_NAME = "chord"
DEFAULT_NUM_BEATS = 4
DEFAULT_POSITION_RESOLUTION = 128
DEFAULT_TICKS_PER_BEAT = 480
MAX_BPM = 200
NUM_BPM_AUGMENT = 2
NUM_KEY_AUGMENT = 6
UNKNOWN = "unknown"
VELOCITY_INTERVAL = 2

MAJOR_KEY = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
MINOR_KEY = [12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]

KEY_MAP = {
    "cmajor": 0,
    "c#major": 1,
    "dbmajor": 1,
    "dmajor": 2,
    "d#major": 3,
    "ebmajor": 3,
    "emajor": 4,
    "fmajor": 5,
    "f#major": 6,
    "gbmajor": 6,
    "gmajor": 7,
    "g#major": 8,
    "abmajor": 8,
    "amajor": 9,
    "a#major": 10,
    "bbmajor": 10,
    "bmajor": 11,
    "cminor": 12,
    "c#minor": 13,
    "dbminor": 13,
    "dminor": 14,
    "d#minor": 15,
    "ebminor": 15,
    "eminor": 16,
    "fminor": 17,
    "f#minor": 18,
    "gbminor": 18,
    "gminor": 19,
    "g#minor": 20,
    "abminor": 20,
    "aminor": 21,
    "a#minor": 22,
    "bbminor": 22,
    "bminor": 23,
}

KEY_NUM_MAP = {v: k for k, v in KEY_MAP.items()}

TIME_SIG_MAP = {
    "4/4": 0,
    "3/4": 1,
    "6/8": 2,
    "12/8": 3,
}

SIG_TIME_MAP = {v: k for k, v in TIME_SIG_MAP.items()}

PITCH_RANGE_MAP = {
    "very_low": 0,
    "low": 1,
    "mid_low": 2,
    "mid": 3,
    "mid_high": 4,
    "high": 5,
    "very_high": 6,
}

INST_MAP = {
    "accordion": 1,
    "acoustic_bass": 3,
    "acoustic_guitar": 3,
    "acoustic_piano": 0,
    "banjo": 3,
    "bassoon": 5,
    "bell": 2,
    "brass_ensemble": 5,
    "celesta": 2,
    "choir": 7,
    "clarinet": 5,
    "drums_full": 6,
    "drums_tops": 6,
    "electric_bass": 3,
    "electric_guitar_clean": 3,
    "electric_guitar_distortion": 3,
    "electric_piano_1": 0,
    "fiddle": 4,
    "flute": 5,
    "glockenspiel": 2,
    "harp": 3,
    "harpsichord": 0,
    "horn": 5,
    "keyboard": 0,
    "mandolin": 3,
    "marimba": 2,
    "nylon_guitar": 3,
    "oboe": 5,
    "organ": 0,
    "oud": 3,
    "pad_synth": 4,
    "percussion": 6,
    "recorder": 5,
    "sitar": 3,
    "string_cello": 4,
    "string_double_bass": 4,
    "string_ensemble": 4,
    "string_ensemble_1": 4,
    "string_ensemble_2": 4,
    "string_viola": 4,
    "string_violin": 4,
    "synth_bass": 3,
    "synth_bass_808": 3,
    "synth_bass_wobble": 3,
    "synth_bell": 2,
    "synth_lead": 1,
    "synth_pad": 4,
    "synth_pluck": 7,
    "synth_voice": 7,
    "timpani": 6,
    "trombone": 5,
    "trumpet": 5,
    "tuba": 5,
    "ukulele": 3,
    "vibraphone": 2,
    "whistle": 7,
    "xylophone": 2,
    "zither": 3,
    "orgel": 2,
    "synth_brass": 5,
    "sax": 5,
    "bamboo_flute": 5,
    "yanggeum": 3,
    "vocal": 8,
    "acoustic_grand_piano": 0,
    "acoustic_guitar_nylon": 3,
    "acoustic_guitar_steel": 3,
    "agogo": 2,
    "alto_sax": 5,
    "applause": 8,
    "bagpipe": 1,
    "baritone_sax": 5,
    "bird_tweet": 2,
    "blown_bottle": 7,
    "brass_section": 5,
    "breath_noise": 3,
    "bright_acoustic_piano": 0,
    "cello": 4,
    "choir_aahs": 7,
    "church_organ": 0,
    "contrabass": 5,
    "distortion_guitar": 3,
    "drawbar_organ": 0,
    "dulcimer": 3,
    "electric_bass_finger": 3,
    "electric_bass_pick": 3,
    "electric_grand_piano": 0,
    "electric_guitar_jazz": 0,
    "electric_guitar_muted": 3,
    "english_horn": 5,
    "ensemble": 5,
    "french_horn": 5,
    "fretless_bass": 3,
    "fx_1_rain": 1,
    "fx_2_soundtrack": 3,
    "fx_3_crystal": 5,
    "fx_4_atmosphere": 3,
    "fx_5_brightness": 7,
    "fx_6_goblins": 7,
    "fx_7_echoes": 7,
    "fx_8_sci-fi": 7,
    "guitar_fret_noise": 3,
    "guitar_harmonics": 3,
    "harmonica": 3,
    "helicopter": 2,
    "honky_tonk_piano": 0,
    "kalimba": 2,
    "koto": 3,
    "lead_1_square": 1,
    "lead_2_sawtooth": 1,
    "lead_3_calliope": 1,
    "lead_4_chiff": 0,
    "lead_5_charang": 3,
    "lead_6_voice": 1,
    "lead_7_fifths": 1,
    "lead_8_bass+lead": 1,
    "melodic_tom": 3,
    "music_box": 0,
    "muted_trumpet": 5,
    "ocarina": 2,
    "orchestra_hit": 4,
    "orchestral_harp": 3,
    "overdriven_guitar": 3,
    "pad_1_new_age": 4,
    "pad_2_warm": 4,
    "pad_3_polysynth": 1,
    "pad_4_choir": 7,
    "pad_5_bowed": 4,
    "pad_6_metallic": 4,
    "pad_7_halo": 4,
    "pad_8_sweep": 4,
    "pan_flute": 5,
    "percussive_organ": 0,
    "piccolo": 5,
    "pizzicato_strings": 4,
    "reed_organ": 0,
    "reverse_cymbal": 4,
    "rock_organ": 0,
    "seashore": 3,
    "shakuhachi": 5,
    "shamisen": 3,
    "slap_bass": 3,
    "soprano_sax": 5,
    "steel_drums": 6,
    "synth_drum": 3,
    "taiko_drum": 6,
    "tango_accordion": 1,
    "telephone_ring": 2,
    "tenor_sax": 5,
    "tinkle_bell": 2,
    "tremolo_strings": 3,
    "tubular_bells": 2,
    "viola": 4,
    "violin": 4,
    "voice_oohs": 7,
    "woodblock": 0,
    "synthbrass": 5,
    "synthstrings_1": 4,
    "synthstrings_2": 4,
    "shanai": 5,
    "clavi": 1
}

# GENRE_MAP = {
#     "rock": 0,
#     "cinematic": 1,
# }

GENRE_MAP =  {
    "cinematic": 0,
    "newage": 0,
    "new_age": 0,
    "electronic": 3,
    "pop": 9,
    "chillout": 6,
    "rock": 10,
    "classical": 0,
    "country": 1,
    "latin": 0,
    "metal": 7,
    "christmas_holiday": 1,
    "folk_world_country": 4,
    "dance": 2,
    "instrumental": 5,
    "soul": 11,
    "rock_pop": 10,
    "soundtrack": 5,
    "reggae": 9,
    "jazz": 6,
    "brazilian": 1,
    "folk": 4,
    "blues": 6,
    "funk_soul": 6,
    "oldie": 8,
    "hiphop": 8,
    "gothic": 0,
    "jpop_jrock": 9,
    "posthardcore": 10,
    "experimental": 3,
    "rnb": 9,
    "stage_screen": 5,
    "christian": 1,
    "easylistening": 1,
    "brass_military": 1,
    "gospel": 11,
    "celtic": 4
}

TRACK_ROLE_MAP = {
    "main_melody": 0,
    "sub_melody": 1,
    "accompaniment": 2,
    "bass": 3,
    "pad": 4,
    "riff": 5,
}

RHYTHM_MAP = {
    "standard": 0,
    "triplet": 1,
}

