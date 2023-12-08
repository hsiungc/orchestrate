# Imports
import os
import time
from retry import retry
import pandas as pd
import openai
import json

# Set openai api key
openai_key = os.environ.get("OPENAI_KEY")
openai.api_key = openai_key

# Prompt
gpt_prompt = 'From the prompt below, extract the following information: key signature, number of measures, BPM, genre, instrument, time signature, minimum velocity, maximum velocity, and set of unique chords. Format the output as a JSON with the following types: {"key signature": string, "number of measures": integer, "BPM": integer, "genre": string, "instrument": string, "time signature": string, "minimum velocity": integer, "maximum velocity": integer, "set of unique chords": list}. If the information is unknown or not specified use the default value from the following dictionary:\n{"key signature":"C major", "number of measures": 8, "BPM":120, "genre":"rock", "instrument":"acoustic grand piano", "time signature":"4/4", "minimum velocity":10, "maximum velocity":127}\n\n'

def user_prompt_extraction(user_prompt, model='gpt-3.5-turbo'):
    prompt = gpt_prompt + user_prompt

    messages = [{'role': 'user', 'content': prompt}]

    response = openai.ChatCompletion.create(model=model, messages=messages)

    return json.loads(response.choices[0].message['content'])

if __name__ == "__main__":
    user_prompt = "Create a captivating 30-second intro for a rock track. With a brisk tempo and a driving rhythm to generate a unique melody. Explore across 14 measures, allowing the chords B, F#, G#, E, and A to harmonize in an unknown pitch range. Set the velocity between 96 to 111 to ensure a dynamic composition. Enjoy the creative journey!"
    
    gpt_response = user_prompt_extraction(user_prompt)
    print(type(gpt_response))
    print(gpt_response)

