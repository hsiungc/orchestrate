"""
    Instantiates Flask application to setup API endpoints
"""
# load system libraries for data post-processing
import os
import sys
import boto3
import tempfile
import json
import re
import subprocess
from io import BytesIO, BufferedReader


# load flask libraries for API endpoints
from flask import Flask, request, send_file
from flask_cors import CORS, cross_origin

# load nlp libraries for text processing 
from plugins.nlp_package.LanguageModel import LanguageModel
from plugins.nlp_package.utils.GenerateChords import chord_selector, generate_chords

# load ComMU class for music generation
from ComMU import ComMU

# Load mido library to merge MIDI files into multi-track MIDI file
import mido
from mido import MidiFile, MidiTrack
from midi2audio import FluidSynth


# load other pertinent libraries
from plugins.ConfigLoader import ConfigLoader

import openai

# grab environment variables
aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
region = os.environ.get('REGION_NAME')
huggingface_apikey = os.environ.get("HUGGINGFACE_API_KEY", None)
openai_apikey = os.environ.get("OPENAI_API_KEY", None)
key = os.environ.get('TEST_KEY')

sys.stdin.reconfigure(encoding="utf-8")
sys.stdout.reconfigure(encoding="utf-8")

application = Flask(__name__)

# OpenAI key setup
openai.api_key = openai_apikey

# download the model
# Read the file from S3
try:
    file_key = 'checkpoint_best.pt'

    # check if the model checkpoint directory exists
    if file_key not in os.listdir('./model_snapshot'):
        # Create an S3 client
        # Specify the bucket name and the file key (path) within the bucket
        # Grab the model checkpoint from S3
        s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=region)
        bucket_name = 'orchestrate-bucket'
        prefix = 'commu-model/checkpoints-above-52000'
    
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)

        # Iterate through the objects and download the model checkpoint
        for obj in response.get('Contents', []):
            fkey = obj['Key'] + file_key
            s3.download_file(bucket_name, fkey , f'./model_snapshot/{file_key}')
            break
        print('File downloaded successfully.')
    else:
        print('Model already downloaded')

except Exception as e:
    print('Error reading file from S3:', e)


# Loading Model Configurations and model states
# grab model dictionary
inst_dict = ConfigLoader().loadYaml("./config/model_config.yml")['INST_PROGRAM']
key_chords_dict = ConfigLoader().loadYaml("./config/model_config.yml")['KEY_CHORDS']
n_jobs = ConfigLoader().loadYaml("./config/model_config.yml")['JOBS']
llm = ConfigLoader().loadYaml("./config/model_config.yml")['LLM']
gpt_template = ConfigLoader().loadYaml("./config/model_config.yml")['TEMPLATE']
model_dict = ConfigLoader().loadYaml("./config/model_config.yml")['MODELS']

# instantiate LanguageModel class object
nlp = LanguageModel(model_dict, huggingface_apikey, openai_apikey, gpt_template, llm, n_jobs)

# instantiate ComMU model class object
commu = ComMU()


# instantiate fluidSynth
fs = FluidSynth()

# configure CORS to allow all origins
cors = CORS(application)
application.config['CORS_HEADERS'] = 'Content-Type'

@application.route("/")
@cross_origin()
def hello():
    return "cross-origin-world established!"

@application.route('/api/generate', methods=['POST'])
def generate_midi_file():
    """
        Generate MIDI files from input arguments
        Input:
            input_args {dict} : input arguments
        Output:
            generated_response {dict} : response dictionary with generated MIDI file data
    """
    """
        Uncder Construction
        TODO: update to post request
        -- from user prompt, extract the necessary input arguments for generation
        # grab the user input NLP prompt from API request
        # user_request_data = request.get_json()['data']
        # user_prompt = user_request_data['prompt']

    """

    # receive the user input data from the API request
    data = request.get_json()
    # check if the API key is valid
    # The above code is checking if the value of the variable `test_key` is not equal to the value of the
    # variable `key`. If they are not equal, it returns a JSON response with an error message "Invalid API
    # Key" and a status code of 401 (Unauthorized).
    test_key=data["key"]
    if test_key != key:
        return json.dumps({"error": "Invalid API Key"}), 401

    try:
       
        # instantiate user NLP prompt input:
        """
            I love playing to jazz music at 4/4 time signature.
            Can you give me a piece of music that is 1-127 velocity with bass? 
            The pitch should be mid with riff. 
            I also want the piece to have a bpm of 125, 8 measures, a minor key, 
            and contains the chords ['C', 'A', 'B']
            I'm in the mood for some cinematic trumpet song at 4/4 time signature, 8 measures, and a BPM of 120 
        """
        input = {"text": data["prompt"]}

        labels = nlp.model_request(input)
        labels['audio_key'] = labels['audio_key'].replace(" ", "").lower()
        print(f"Level 1 NLP Generated Labels: {labels}")

        # default diagram when None
        for label, value in labels.items():
            if value in [None, []]:
                if label == 'bpm': 
                    labels[label] = 120
                elif label == 'audio_key': 
                    labels[label] = "cmajor"
                elif label == 'num_measures':
                    labels[label] = 8
                elif label == 'genre':
                    labels[label] = "cinematic"
                elif label == 'inst':
                    labels[label] = "acoustic_grand_piano"
                elif label == 'time_signature':
                    try:
                        labels[label] = re.findall(r'\d+/\d+',  data["prompt"])[0]
                    except:
                        labels[label] = "4/4"
                elif label == 'min_velocity':
                    labels[label] = 40
                elif label == 'max_velocity':
                    labels[label] = 127
                elif label == 'chords':
                    # activate chord selector
                    try:
                        labels[label] = chord_selector(labels['audio_key'], key_chords_dict)
                    except Exception as e:
                        print(e)
                        labels[label] = ["Am", "G", "F", "E"]

        # print the final labels
        print( f"Final Labels: {labels}")


        # Programmatically process chord progressions
        try:
            labels['num_measures'] = int(labels['num_measures'])
            # map the number of measures properly 4-16
            if labels['num_measures'] >= 0 and labels['num_measures'] < 8:
                labels['num_measures'] = 4
            elif labels['num_measures'] >= 8 and labels['num_measures'] < 16:
                labels['num_measures'] = 8
            elif labels['num_measures'] >= 16:
                labels['num_measures'] = 16
            # turn string of a list into a list
            if type(labels['chords']) == str:
                labels['chords'] = labels['chords'].replace("'", "").replace("[", "").replace("]", "").split(",")
            chord_progression = generate_chords(labels['chords'], int(labels['num_measures']), labels['time_signature'])
        except Exception as e:
            print(e) 
            chord_progression = "Am-Am-Am-Am-Am-Am-Am-Am-G-G-G-G-G-G-G-G-F-F-F-F-F-F-F-F-E-E-E-E-E-E-E-E-Am-Am-Am-Am-Am-Am-Am-Am-G-G-G-G-G-G-G-G-F-F-F-F-F-F-F-F-E-E-E-E-E-E-E-E"
        

        # initialize model and input variables
        model_args, _ = commu.parse_args()["model_args"].parse_known_args(args=["--checkpoint_dir", f"./model_snapshot/{file_key}"])
        input_args, _ = commu.parse_args()["input_args"].parse_known_args(args=["--output_dir", "./output",
                                                                        "--bpm", f"{labels['bpm']}",
                                                                        "--audio_key", f"{labels['audio_key']}",
                                                                        "--time_signature", f"{labels['time_signature']}",
                                                                        "--pitch_range", "mid",
                                                                        "--num_measures", f"{labels['num_measures']}",
                                                                        "--inst", f"{labels['inst']}",
                                                                        "--genre", f"{labels['genre']}",
                                                                        "--min_velocity", f"{labels['min_velocity']}",
                                                                        "--max_velocity", f"{labels['max_velocity']}",
                                                                        "--track_role", f"main_melody",
                                                                        "--chord_progression", f"{chord_progression}",
                                                                        "--num_generate", "1"])
        # generate MIDI files based on user input
        midi_files_dict = commu.generate(model_args, input_args)

        # fetch the generated MIDI file from the dictionary
        original_midi_file = midi_files_dict[0]

        # parse the proper instrument from the user input
        # parse_inst = ParseInst(inst_dict)
        # original_midi_file = parse_inst.change_instrument(original_midi_file, labels['inst'])
        for i in range(len(original_midi_file.instruments)):
            original_midi_file.instruments[i].program = inst_dict[labels['inst']]


        # Create a temporary file to save the MIDI data
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mid", mode='wb') as temp_midi_file:
            # Write the MIDI data directly to the file
            # original_midi_file.dump(temp_midi_file.name)

            # Open the file in binary write mode and save the MIDI data
            with open(temp_midi_file.name, 'wb') as midi_file:
                original_midi_file.dump(midi_file.name)

                # Set appropriate HTTP headers for binary response
                response = send_file(midi_file.name, as_attachment=True)
                response.headers['Content-Disposition'] = 'attachment; filename=output.mid'
                response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
                response.headers['Pragma'] = 'no-cache'
                response.headers['Content-Type'] = 'audio/midi'
                print("MIDI file send successfully")
        return response
    
    except Exception as e:
        print(e)
        return json.dumps({f"error": f"Error {e} generating MIDI file"}), 500


@application.route('/api/fusion', methods=['POST'])
def overlay_midi_files():
    """
        Overlay multiple user input MIDI files together
        Input:
            input_args {dict} : input arguments
        Output:
            generated_response {dict} : response dictionary with generated MIDI file data
    """
    # 1. Grab the files from POST request
    midi_file_list = request.files

    # 2. Create an empty MIDI file to store each file in uploaded_files as individual tracks
    main_midi_file = MidiFile()

    # 3. Iterate through each track and add the MIDI data
    for file_id in midi_file_list:
        file = midi_file_list[file_id]
        try:
            # Open each MIDI file
            midi_file_data = BytesIO(file.read())
            midi_file = mido.MidiFile(file=BufferedReader(midi_file_data))
            
            # Create a new track for each MIDI file
            new_track = MidiTrack()
            main_midi_file.tracks.append(new_track)

            # Append each track from the MIDI file to the merged track
            for track in midi_file.tracks:
                new_track.extend(track)

        except Exception as e:
            print(e)
            return json.dumps({"error": "Error reading file from S3"}), 500        
                

    # 3. Save the merged MIDI file
    # Create a temporary file to save the MIDI data
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mid", mode='wb') as temp_midi_file:
        # Write the MIDI data directly to the file
        # original_midi_file.dump(temp_midi_file.name)

        # Open the file in binary write mode and save the MIDI data
        with open(temp_midi_file.name, 'wb') as midi_file:
            main_midi_file.save(midi_file.name)

            # Set appropriate HTTP headers for binary response
            response = send_file(midi_file.name, as_attachment=True)
            response.headers['Content-Disposition'] = 'attachment; filename=output.mid'
            response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Content-Type'] = 'audio/midi'

    return response


@application.route('/api/convert-to-wave', methods=['POST'])
def convert_to_wav():

    try:
        # Assuming the MIDI file is sent in the request
        midi_data = request.files['midiFile']

        # Save the MIDI data to a file
        # Convert MIDI to Audio using FluidSynth
        midi_file_path = './output/input.mid'
        audio_file_path = './output/output.wav'
        with open(midi_file_path, 'wb') as midi_file:
            midi_file_data = BytesIO(midi_data.read())
            midi_file = mido.MidiFile(file=BufferedReader(midi_file_data))
            midi_file.save(midi_file_path)
            fs.midi_to_audio(midi_file_path, audio_file_path)

       # Respond with the download link
        response = send_file(audio_file_path, as_attachment=True)
        response.headers['Content-Disposition'] = 'attachment; filename=distorted_output.wav'
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Content-Type'] = 'audio/wav'
        return response
    except Exception as e:
        print(f'Error processing MIDI: {str(e)}')
        return json.dumps({'error': 'Error downloading file.'}), 500



@application.route('/api/applysynth', methods=['POST'])
def apply_synth():

    try:
        # Assuming the MIDI file is sent in the request
        midi_data = request.files['midiFile']
        synth_type = request.form.get('synthType', '')
        # oscillator_type = request.form.get('oscillatorType', '')
        volume = request.form.get('volume', '')
        delay_amount = request.form.get('delay', '')
        distortion_level = request.form.get('distortion', '')
        reverb_amount = request.form.get('reverb', '')
        auto_filter_amount = request.form.get('autoFilter', '')
        tremolo_amount = request.form.get('tremolo', '')
        

        
        # Save the MIDI data to a file
        # Convert MIDI to Audio using FluidSynth
        midi_file_path = './output/input.mid'
        audio_file_path = './output/output.wav'
        with open(midi_file_path, 'wb') as midi_file:
            midi_file_data = BytesIO(midi_data.read())
            midi_file = mido.MidiFile(file=BufferedReader(midi_file_data))
            midi_file.save(midi_file_path)
            fs.midi_to_audio(midi_file_path, audio_file_path)

        # Apply distortion using SoX
        # distortion_level = '20'  # Adjust as needed
        updated_wav = "./output/updated_wav.wav"
        subprocess.run(['sox', audio_file_path, updated_wav, 'vol', str(volume)])
        subprocess.run(['sox', audio_file_path, updated_wav, 'delay', str(delay_amount)])
        subprocess.run(['sox', audio_file_path, updated_wav, 'overdrive', str(distortion_level)])
        subprocess.run(['sox', audio_file_path, updated_wav, 'reverb', str(reverb_amount)])
        subprocess.run(['sox', audio_file_path, updated_wav, 'bass', str(auto_filter_amount)])
        subprocess.run(['sox', audio_file_path, updated_wav, 'tremolo', str(tremolo_amount)])

        if synth_type == 'sine':
            duration = 5
            frequency = 440
            amplitude = 0.5
            subprocess.run(['sox', audio_file_path, updated_wav, 'synth', str(duration), 'sin', str(frequency), 'amplitude', str(amplitude)])

        elif synth_type == 'square':
            duration = 5
            frequency = 880
            amplitude = 0.7
            subprocess.run(['sox', audio_file_path, updated_wav, 'synth', str(duration), 'square', str(frequency), 'amplitude', str(amplitude)])

        elif synth_type == 'triangle':
            duration = 5
            frequency = 220
            amplitude = 0.6
            subprocess.run(['sox', audio_file_path, updated_wav, 'synth', str(duration), 'saw', str(frequency), 'amplitude', str(amplitude)])


        # Respond with the download link
        response = send_file(updated_wav, as_attachment=True)
        response.headers['Content-Disposition'] = 'attachment; filename=distorted_output.wav'
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Content-Type'] = 'audio/wav'

        return response
    except Exception as e:
        print(f'Error processing MIDI: {str(e)}')
        return json.dumps({'error': 'Error downloading file.'}), 500


if __name__ == '__main__':
    """
        Use for Port Declaration and python run
    """
    # TODO: Add dynamic host once deployed
    from waitress import serve
    serve(application, host="0.0.0.0", port=5000)