"""
    MetaInputParser
    Plugin class to parse and validate input data
"""
import argparse
from typing import Dict

from commu.midi_generator.generate_pipeline import MidiGenerationPipeline
from commu.preprocessor.utils import constants


class ComMU():
    def __init__(self):
        """Constructor for MetaInputParser class"""
        pass

    def parse_args(self) -> Dict[str, argparse.ArgumentParser]:
        """
            Parse and validate input arguments
            Input arguments are divided into two categories:
                1. Model Arguments: 
                    - Model Arguments are used to load the model from checkpoint
                2. Input Arguments
                    - Directory to save generated midi files
                    - meta data infomration for seeded generation
                    - Inference arguments for generation
            Output:
                arg_dict: Dict[str, argparse.ArgumentParser]
        """
        model_arg_parser = argparse.ArgumentParser(description="Model Arguments")
        input_arg_parser = argparse.ArgumentParser(description="Input Arguments")

        # Model Arguments
        model_arg_parser.add_argument("--checkpoint_dir", type=str)

        # Input Arguments
        input_arg_parser.add_argument("--output_dir", type=str, required=True)

        ## Input meta
        input_arg_parser.add_argument("--bpm", type=int)
        input_arg_parser.add_argument("--audio_key", type=str, choices=list(constants.KEY_MAP.keys()))
        input_arg_parser.add_argument("--time_signature", type=str, choices=list(constants.TIME_SIG_MAP.keys()))
        input_arg_parser.add_argument("--pitch_range", type=str, choices=list(constants.PITCH_RANGE_MAP.keys()))
        input_arg_parser.add_argument("--num_measures", type=float)
        input_arg_parser.add_argument(
            "--inst", type=str, choices=list(constants.INST_MAP.keys()),
        )
        input_arg_parser.add_argument(
            "--genre", type=str, default="cinematic", choices=list(constants.GENRE_MAP.keys())
        )
        input_arg_parser.add_argument(
            "--track_role", type=str, choices=list(constants.TRACK_ROLE_MAP.keys())
        )
        input_arg_parser.add_argument(
            "--rhythm", type=str, default="standard", choices=list(constants.RHYTHM_MAP.keys())
        )
        input_arg_parser.add_argument("--min_velocity", type=int, choices=range(1, 128))
        input_arg_parser.add_argument("--max_velocity", type=int, choices=range(1, 128))
        input_arg_parser.add_argument(
            "--chord_progression", type=str, help='Chord progression ex) C-C-E-E-G-G ...'
        )
        # Inference 시 필요 정보
        input_arg_parser.add_argument("--num_generate", type=int)
        input_arg_parser.add_argument("--top_k", type=int, default=32)
        input_arg_parser.add_argument("--temperature", type=float, default=0.95)

        arg_dict = {
            "model_args": model_arg_parser,
            "input_args": input_arg_parser
        }
        return arg_dict


    def generate(self, model_args: argparse.Namespace, input_args: argparse.Namespace):
        """
            From input arguments, generate midi files
            Input:
                model_args {argparse.Namespace} : model path 
                input_args {argparse.Namespace} : output path & MIDI meta parameters
        """
        pipeline = MidiGenerationPipeline()
        pipeline.initialize_model(vars(model_args))
        pipeline.initialize_generation()

        inference_cfg = pipeline.model_initialize_task.inference_cfg
        model = pipeline.model_initialize_task.execute()

        encoded_meta = pipeline.preprocess_task.execute(vars(input_args))
        input_data = pipeline.preprocess_task.input_data

        pipeline.inference_task(
            model=model,
            input_data=input_data,
            inference_cfg=inference_cfg
        )
        sequences = pipeline.inference_task.execute(encoded_meta)

        pipeline.postprocess_task(input_data=input_data)
        file_path = pipeline.postprocess_task.execute(
                        sequences=sequences,
                    )
        return file_path

