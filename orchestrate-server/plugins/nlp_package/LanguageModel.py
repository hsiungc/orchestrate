import os
import json
import warnings
import logging

# from dotenv import load_dotenv
from joblib import Parallel, delayed

import openai
from huggingface_hub import InferenceClient
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    pipeline
)

# load_dotenv()
warnings.filterwarnings("ignore")
logging.getLogger("transformers").setLevel(logging.ERROR)

# HuggingFace client
# hugging face key 
hf_key = os.environ.get("HUGGINGFACE_API_KEY", None)

# OpenAI key
openai.api_key = os.environ.get("OPENAI_API_KEY", None)



class LanguageModel:
    def __init__(self, models: dict, hf_key: str, llm_key: str, template: str, llm, n_jobs: int):
        self.models = models
        self.hf_key_check = hf_key
        self.key_check = llm_key
        self.template = template
        self.llm_check = llm
        self.num_jobs = n_jobs

    def task_call(self, input: str, model_key: str, model: str) -> str:
        try:
            if self.key_check is not None and model in self.llm_check:
                # ChatGPT requests
                prompt = self.template + input["text"]
                messages = [{"role": "user", "content": prompt}]
                response_content = openai.ChatCompletion.create(model=model, messages=messages)
                response_json = json.loads(response_content.choices[0].message["content"])
                
                return response_json[model_key]
        
            else:
                # HuggingFace Single Task model requests
                client = InferenceClient(token=self.hf_key_check)
                response_bytes = client.post(json=input, model=model)
                response_json = json.loads(response_bytes)

                
                return response_json[0]["label"]
        
        except Exception as e:
            print(e)
            print(f"Model {model_key} call error: check model name and key information.")
    
    def model_request(self, input: str) -> dict:
        responses = Parallel(n_jobs=self.num_jobs)(delayed(self.task_call)(input, key, model) for key, model in self.models.items())
        output_dict = dict(zip(self.models.keys(), responses))
        
        return output_dict

class LanguageModelPipeline:
    def __init__(self, models: dict, hf_key: str, llm_key: str, template: str, llm, n_jobs: int):
        self.models = models
        self.hf_key_check = hf_key
        self.key_check = llm_key
        self.template = template
        self.llm_check = llm
        self.num_jobs = n_jobs


    def task_call(self, input: str, model_key: str, model: str) -> str:
        try:
            if self.key_check is not None and model in self.llm_check:
                # ChatGPT requests
                prompt = self.template + input["text"]
                messages = [{"role": "user", "content": prompt}]
                response_content = openai.ChatCompletion.create(model=model, messages=messages)
                response_json = json.loads(response_content.choices[0].message["content"])
                
                return response_json[model_key]
        
            else:
                # HuggingFace Single Task model requests
                response = model(input["text"])
                return response[0][0]["label"]
        
        except Exception as e:
            print(e)
            print(f"Model {model_key} call error: check model name and key information.")
    
    def model_request(self, input: str) -> dict:
        responses = Parallel(n_jobs=self.num_jobs)(delayed(self.task_call)(input, key, model) for key, model in self.models.items())
        output_dict = dict(zip(self.models.keys(), responses))
        
        return output_dict


def load_pipeline(model):
    bert_model = AutoModelForSequenceClassification.from_pretrained(model)
    bert_tokenizer = AutoTokenizer.from_pretrained(model)
    classifier = pipeline(
        task="text-classification",
        model=bert_model,
        tokenizer=bert_tokenizer,
        top_k=1
    )
    
    return classifier
    
    
if __name__ == "__main__":
    input = {"text": "I love playing to jazz music at 3/4 time signature. Can you give me a piece of music \
                        that is 1-127 velocity with bass? The pitch should be mid with riff. I also want 125 bpm in 8 measures \
                        in a minor key and chords of ['C','A','B']"}
    
    # Move the below to config yaml
    gpt_template = 'From the prompt below, extract the following information: key signature (audio_key), number of measures (num_measures), \
        BPM, genre, instrument (inst), time signature (time_signature), minimum velocity (min_velocity), maximum velocity (max_velocity), \
        and unique chords (chords). Format the output as a JSON with the following types: {"audio_key": string, "num_measures": integer, \
        "bpm": integer, "genre": string, "inst": string, "time_signature": string, "min_velocity": integer, "max_velocity": integer, \
        "chords": list}. If the information is unknown or not specified use the default value from the following dictionary: \
        \n{"key_signature":"C major", "num_measures": 8, "bpm":120, "genre":"rock", "inst":"acoustic grand piano", \
            "time_signature":"4/4", "min_velocity":10, "max_velocity":127}\n\n'

    model_dict = {
        "audio_key": "hsiungc/bert-audio-key",
        "num_measures": "hsiungc/bert-num-measures",
        "bpm": "hsiungc/bert-bpm",
        "time_signature": "gpt-3.5-turbo",
        "genre": "hsiungc/bert-genre",
        "inst": "hsiungc/bert-inst",
        "min_velocity": "hsiungc/bert-min-velocity",
        "max_velocity": "hsiungc/bert-max-velocity",
        "chords": "gpt-3.5-turbo",
    }
    n_jobs = 10
    llm = {"gpt-3.5-turbo", "gpt-3.5-turbo-1106", "gpt-4", "gpt-4-1106-preview"}
    
    # LanguageModel class
    nlp = LanguageModel(model_dict, hf_key, openai.api_key, gpt_template, llm, n_jobs)
    labels = nlp.model_request(input)
    print(labels)
    
    # LanguageModelPipeline class
    pipeline_dict = {key: load_pipeline(model) if model not in llm else model for key, model in model_dict.items()}
    hf_nlp = LanguageModelPipeline(pipeline_dict, hf_key, openai.api_key, gpt_template, llm, n_jobs)
    predictions = hf_nlp.model_request(input)
    print(predictions)
