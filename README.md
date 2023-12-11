<img src='https://github.com/hsiungc/orchestrate/blob/main/orchestrate-logo.png' width="492" height="288" alignment="center">

# Orchestrate - Capstone Project (Fall 2023)

## Public-Facing GitHub Repository

### Andy Fiegleman, Casey Hsiung, Dakota Postere-Ramos, James Meyer, Ken Trinh

<br>

[Website](https://orchestratemusic.com/) | [Demo](https://orchestrate.vercel.app/)


Individuals aspiring to create music face the challenge of either mastering multiple instruments required for their compositions or relying on digital tools for music production. Orchestrate harnesses the power of machine learning and natural language processing (NLP) to develop a prompt-responsive music generation product. This innovative platform empowers users to create and layer diverse music pieces, crafting personalized arrangements that can be utilized for jamming, sparking musical inspiration, or simply enjoying music in its own right.

<br>

### Setup Instructions

To run the server and client locally, follow the below steps. An OpenAI key (```OPENAI_API_KEY```) is required to use ChatGPT.

#### Orchestrate Client

1. Install Node.js and npm from [here](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm).
2. Navigate to the ```orchestrate-client``` directory.
3. Run the following commands:
```
npm install
npm run start
```
4. A browser should open at the http://localhost:3000 address.
5. Following the frontend instructions will allow you to play and download a music file by submitting a text prompt.


#### Orchestrate Server

1. Install Flask from [here](https://flask.palletsprojects.com/en/3.0.x/installation/).
2. Navigate to the ```orchestrate-server``` directory.
3. Run the following commands:
```
pip install -r requirements.txt
flask run
```
4. We recommend using a simple tool such as [Postman](https://web.postman.co/) to send POST requests to the Orchestrate server at http://localhost:5000/api/generate.

<br>

### Citations

[Hyun, L., Kim, T., Kang, H., Ki, M., Hwang, H., Park, K., ... & Kim, S. J. (2022). ComMU: Dataset for Combinatorial Music Generation. arXiv preprint arXiv:2211.09385.](https://arxiv.org/pdf/2211.09385.pdf)

[Ens, J., & Pasquier, P. (n.d.). Building the MetaMIDI dataset: Linking Symbolic and Audio Musical Data. Proceedings of the 22nd ISMIR Conference. https://archives.ismir.net/ismir2021/paper/000022.pdf](https://archives.ismir.net/ismir2021/paper/000022.pdf)

<br>

### Licenses & User Agreements

<b>ComMU License </b><br>
[ComMU GitHub](https://pozalabs.github.io/ComMU/) <br>
[ComMU Demo](https://pozalabs.github.io/ComMU/)

The ComMU dataset is released under Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License (CC BY-NC-SA 4.0). It is provided primarily for research purposes and is prohibited to be used for commercial purposes.

<br>

<b> MetaMIDI Copyright </b><br>
[MetaMIDI Dataset Github](https://github.com/jeffreyjohnens/MetaMIDIDataset#copyright) <br>
[MetaMIDI Dataset](https://zenodo.org/records/5142664)

Since we did not transcribe any of the MIDI files in the MetaMIDI Dataset, we provide a list of all the Copyright meta-events in the dataset to acknowledge the original authors of the files.
