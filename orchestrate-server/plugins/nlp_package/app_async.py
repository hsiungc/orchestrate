import json
from dotenv import load_dotenv
import asyncio

from huggingface_hub import AsyncInferenceClient, InferenceTimeoutError
from grouphug import AutoMultiTaskModel, DatasetFormatter

load_dotenv()

client = AsyncInferenceClient(timeout=60)


# Load models
# Place into main script
# Multitask BERT
# multitask_path = "s3://orchestrate-bucket/bert/multitask/saved/checkpoint-195000/"
# multitask_model = AutoMultiTaskModel.from_pretrained(multitask_path)

# Single Task BERTs
async def singletask_call(input: dict, model: str) -> str:
    try:
        response_bytes = await client.post(json=input, model=model)
        response_json = json.loads(response_bytes)
        return response_json[0]["label"]
    
    except InferenceTimeoutError:
        print("Model timed out after 60 seconds.")
        
async def model_request(input: dict, models: dict) -> dict:
    try:
        responses = [singletask_call(input, model) for model in models.values()]
        outputs = await asyncio.gather(*responses)
        
        output_dict = dict(zip(models.keys(), outputs))
        return output_dict
    
    except InferenceTimeoutError:
        print("Model timed out after 60 seconds.")


if __name__ == "__main__":
    input = {"text": "I love playing to jazz music at 4/4 time signature. Can you give me a piece of music \
                        that is 1-127 velocity with bass? The pitch should be mid with riff. I also want 125 bpm in 8 measures \
                        in a minor key and chords of ['C','A','B']"}
    
    model_dict = {
        "audio_key": "hsiungc/bert-audio-key",
        "num_measures": "hsiungc/bert-num-measures",
        "bpm": "hsiungc/bert-bpm",
        "genre": "hsiungc/bert-genre",
        "inst": "hsiungc/bert-inst",
        "min_velocity": "hsiungc/bert-min-velocity",
        "max_velocity": "hsiungc/bert-max-velocity",
        "chord": "hsiungc/bert-chord",
    }
    
    event_loop = asyncio.get_event_loop()
    labels = event_loop.run_until_complete(model_request(input, model_dict))
    print(labels)