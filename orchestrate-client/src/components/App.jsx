import React, { useState, useEffect } from "react";

// Material UI components
import { 
    Button, CircularProgress, Modal, 
    Paper, InputBase, 
    Slide} from '@mui/material';

import { Audiotrack }  from '@mui/icons-material';

// import music from './local/music.mp3'
import MidiPlayer from 'react-midi-player';
import { parseArrayBuffer } from "midi-json-parser";
import { encode } from "json-midi-encoder";

// import DAW libs
import { Midi } from '@tonejs/midi';
import Synthesizer from "./DAW/Synthesizer";


import logo from './local/Logo-removebg.png'

function App() {

    // initialize user input state
    const [userPrompt, setUserPrompt] = useState(""); // NLP input state
    const [key, setKey] = useState(""); // API key state

    // default MIDI data to file parameters
    const [customMidiFile, setCustomMidiFile] = useState({
        replaySpeed: 1,
        key: 0
    }); // MIDI Data File state


    // single gnerated MIDI file state
    const [data, setData] = useState("");   // MIDI Data state
    const [midiFile, setMIDIFile] = useState(null);   // MIDI Data state
    const [blobFile, setBlobFile] = useState(null);   // MIDI Data state
    const [url, setUrl] = useState(null);   // MIDI Data URL state

    // single generated Wave file state
    const [wavUrl, setWavUrl] = useState(null);   // MIDI Data URL state

    // fusion MIDI file state
    const [files, setFiles] = useState([]); // MIDI Data files state

    // MIDI synthesizer state
    const [steps, setSteps] = useState([]); // MIDI Data steps state
    const [tempo, setTempo] = useState(0); // MIDI Data tempo state

    const [progress, setProgress] = useState(false); // progress bar state
    const [open, setOpen] = useState(true); // confirm dialog state

    // information cards every time their state is change
    useEffect(() => { 
    }, []);


    /**
     * Function to handle user input parsing into state variable
     * @param {*} e: user natrual language input
     */
    const handleInputChange = (e) => {
        e.preventDefault();
        setUserPrompt(e.target.value);
    }

    /**
     * Function to handle Test API Key input
     * TODO: removel uplon publish
     * @param {*} e: API key string
     */
    const handleInputKeyChange = (e) => {
        e.preventDefault();
        setKey(e.target.value);
    }

    /**
     * Function to handle Modal Window Close
     */
    const handleClose = () => {
        setOpen(false);
    };


    /**
     * Function to calculate frequency of MIDI number for Bandpass filter
     */
    const midiToFrequency = (midi) => {
        return 400 * Math.pow(2, (midi - 69) / 12);
    };
    
    /**
     * Function for Bandpass filter
     */
    const bandpassFilter = (note, filterFrequency, qualityFactor) => {
        const startTime = note.ticks * (60 / note.tempo);
        const endTime = startTime + note.duration;

        for (let time = startTime; time < endTime; time += 0.001) {
            const frequency = midiToFrequency(note.midi);
            const filterResponse = Math.exp(-0.5 * Math.pow((frequency - filterFrequency) / qualityFactor, 2));
            // const filterAmplitude = note.velocity * filterResponse;

            const filteredFrequency = frequency * filterResponse;

            return filteredFrequency
        }
    };

    /**
     * Constants for Bandpass filter
     */
    const filterFrequency = 1450;
    const qualityFactor = 0.5;

    /**
    * Function to parse MIDI file into a sequence of notes
    * @param {*} midiData: MIDI datafile
    * @returns {Array} seq: sequence of notes
    */
    const parseMidi = (midiData) => {
        if (midiData) {
            const midi = new Midi(midiData);
            const tempo = midi.header.tempos[0].bpm; // Get the tempo bpm of the MIDI file
            
            // update MIDI file state
            setMIDIFile(midi);
            setTempo(tempo);


            let seq = [];

            midi.tracks?.forEach((track) => {
                track.notes.forEach((note) => {

                    // Parse the note data into a list of sequences
                    // const { name, duration, velocity} = note;
                    let seq_tempate = {
                        name: note.name, 
                        duration: Math.round(note.duration * (60 / tempo) * 10) / 10, 
                        velocity: Math.ceil(note.velocity),
                        midi: note.midi,
                        ticks: note.ticks,
                        durationTicks: note.durationTicks,
                        tempo: tempo
                    };

                    seq_tempate.filteredFrequency = bandpassFilter(note, filterFrequency, qualityFactor);

                    seq.push(seq_tempate);

                });
            });
            return seq;
        }
    }

    /**
     * Function to encode MIDI file into a sequence of notes
     * @param {*} fileMidi: MIDI datafile
     * @param {*} key: key to transpose the MIDI file
     * @param {*} replaySpeed: speed to replay the MIDI file
     */
    const handleChangeMidiFile = (fileMidi, { key, replaySpeed }) => {
        if (fileMidi) {
            const reader = new FileReader();
            reader.onload = async (event) => {
                parseArrayBuffer(event.target.result).then((json) => {
                    // Iterate through all tracks and modify events
                    json.tracks?.[0].map((event) => {
                        if (event.noteOn || event.noteOff) {
                            event.delta = Math.round(event.delta / replaySpeed);
                            if (event.noteOn) {
                                event.noteOn.noteNumber += key;
                                event.noteOn.frequency = bandpassFilter(event.noteOn.frequency, filterFrequency, qualityFactor);
                            } else {
                                event.noteOff.noteNumber += key;
                                event.noteOff.frequency = bandpassFilter(event.noteOff.frequency, filterFrequency, qualityFactor);
                            }
                        }
                        return event;
                    });

                    // encode all modified tracks
                    encode(json).then((midiFile) => {
                        // encode MIDI file to Uint8Array
                        setData(""); // clear the data state
                        const midiArray = new Uint8Array(midiFile);
                        setData(midiArray);


                        // conver midi to WAV and then create a url from blob to be use for download
                        // setWavUrl(null);
                        // const midi = new Midi(midiArray);
                        // const wavData = convertMidiToWav(midi);
                        // const wavBlob = new Blob([wavData], { type: 'audio/wav' });
                        // const wavFileDownload = window.URL.createObjectURL(wavBlob);
                        // setWavUrl(wavFileDownload);


                        // parse MIDI file into a sequence of notes
                        setSteps([]);
                        const seq = parseMidi(midiFile);
                        setSteps(seq);
                    });
                });
            };
            reader.readAsArrayBuffer(fileMidi);
        }
    };


    /**
     * Function to handle the Generation button click
     * @param {*} e 
     */
    const handleGenerationClick = async (e) => {
        e.preventDefault();
        setProgress(true);
        try {
            // build the post data to be sent to the server api
            const postData = {
                method:'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    key: 'W210-API-TEST-KEY',
                    prompt: userPrompt
                })
            };
            // initiate fetch request on the server api
            // const response = await fetch('/api/generate', postData);
            const response = await fetch('https://api.orchestrate-api-server.com/api/generate', postData);

            // raise a popup if response is not 200
            if (response.status !== 200){
                alert("Error " + response.status + ": Please Refresh the Page and Try Again");
            } else {
                //Begin parsing the response for immediate playback
                const blob = await response.blob();
                setBlobFile(blob);

                // create a url from blob to be use for download
                const midiFileDownload = window.URL.createObjectURL(blob);
                setUrl(midiFileDownload);

                // create a file from blob to be use for playback
                const file = new File([blob], 'output.mid', { type: 'audio/midi' });

                // set the file to be played
                handleChangeMidiFile(file, customMidiFile);

                // store the generated file for fusion
                setFiles((prevFiles) => [...prevFiles, file]);
            }

        } catch (error) {
            console.error('Error fetching file:', error);
        }

        // wait until operation is complete
        setProgress(false);
    };


    /**
     * Function to handle Fusion of multiple MIDI files
     * @param {*} e: user files upload
     */
    const handleFusion = async (e) => {
        e.preventDefault();
        console.log(`Begin Fusion On ${files.length} files`);
        setProgress(true);
        console.log(files)


        try {
            // convert files to form data
            const formData = new FormData();
            files.forEach((file, index) => {
                formData.append(`file${index}`, file);
            });

            console.log(formData);

            // build the post data to be sent to the server api
            const postData = {
                method:'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: formData
            };
            // initiate fetch request on the api
            const response = await fetch('/api/fusion', postData);
            
            if (response.status !== 200){
                alert("Error " + response.status + ": Prompt Error: Please Refresh the Page and Try a Different Prompt");
            } else {
                //Begin parsing the response for immediate playback
                const blob = await response.blob();

                // create a file from blob to be use for playback
                const file = new File([blob], 'output.mid', { type: 'audio/midi' });

                // set the file to be played
                handleChangeMidiFile(file, customMidiFile);

                // create a url from blob to be use for download
                const midiFileDownload = window.URL.createObjectURL(blob);
                setUrl(midiFileDownload);
            }
        } catch (error) {
            console.error('Error fetching file:', error);
        }

        // wait until operation is complete
        setProgress(false);
    }


    
    const convertToWav = async (e) => {
        e.preventDefault();
        setProgress(true);
        try {
            // convert files to form data
            // create a form data object to send to the server api
            // the form data object will contain the midi file
            const file = new File([blobFile], 'output.mid', { type: 'audio/midi' });
            const formData = new FormData();
            formData.append('midiFile', file);


            // build the post data to be sent to the server api
            const postData = {
                method:'POST',
                body: formData
            };
            // initiate fetch request on the server api
            // const response = await fetch('/api/applysynth', postData);
            const response = await fetch('https://api.orchestrate-api-server.com/api/convert-to-wave', postData);


            if (response.status === 200){
                //Begin parsing the response for immediate playback
                const blob = await response.blob();
                // create a url from blob to be use for download
                const midiFileDownload = window.URL.createObjectURL(blob);
                setWavUrl(midiFileDownload);
            }

        } catch (error) {
            alert("Error "+ error);

        }
        setProgress(false);

    }


    return (
        <section className="color-section" id="title">
            <div className="container-fluid">
                <Modal
                    open={open}
                    aria-labelledby="modal-modal-title"
                    aria-describedby="modal-modal-description"
                >
                    <div className="shadow-lg bg-white rounded-md mx-40 mt-40">
                        {/* <Typography id="modal-modal-title px-20" variant="h6" component="h2"> */}
                        <h1>ORCHESTRATE USE AGREEMENT:</h1>
                        {/* </Typography> */}
                        {/* <Typography id="modal-modal-description px-20" sx={{ mt: 2 }}> */}
                        <br />
                        <h2>By using The Orchestrate Generative Music Service, you agree to the following terms:</h2>
                        <p>You are granted access for non-exclusive, personal, non-commercial use only. 
                        You may not reverse engineer, modify, or use the tool for unlawful purposes. 
                        All intellectual property rights belong to us or lawful partners. 
                        We may provide updates, but we do not guarantee the tool's uninterrupted functionality. 
                        The tool is provided "as is," and we disclaim any warranties. We are not liable for any damages. 
                        This agreement is effective until terminated, and violations may lead to termination.
                        </p>
                        <br />
                        <h2>NO COLLECTION OF PERSONAL USER DATA:</h2>
                        <p>We do not collect, store, or process any personal user data through Orchestrate. 
                        Your privacy is important to us, and we are committed to ensuring that your personal information remains confidential. 
                        The app operates on a "data minimal" principle, meaning we only access and use information necessary for its core functionality.</p>
                        <br />
                        <h2>DATA SECURITY:</h2>
                        <p>While using Orchestrate, any data processed or generated (e.g. MIDI files) 
                        remain on your device and are not transmitted to our servers. 
                        We take reasonable measures to ensure the security of your information, 
                        however, we cannot guarantee the absolute security of data transmission over the Internet.</p>
                        {/* </Typography> */}
                        <Button onClick={handleClose}>Accept</Button>
                    </div>
                </Modal>
                {/* <MenuLinks isAuthenticated={props.isAuthenticated}/> */}
                <div className="flex-warp justify-center mx-20 mt-10">
                    {/* <div className="w-full max-w-lg"> */}
                    <Slide direction="down" in={true} timeout={1000}>
                        <div className="shadow-lg bg-neutral-300 rounded-md px-20 pt-6 pb-8 mb-4 mx-20">
                            <div className="flex justify-center px-2 pt-6 pb-8 mb-4">
                                <img src={logo} alt="Logo" />
                            </div>
                            <div className="mb-5">
                                {/* <label className="block text-black text-lg font-bold mb-2">Let Us Orchestrate Your Tune</label> */}
                                {/* <Paper component="form" 
                                    className="flex justify-center h-10 w-40 mb-2"
                                >
                                    <InputBase
                                        sx={{ ml: 1, flex: 1 }}
                                        placeholder="API Key"
                                        inputProps={{ 'aria-label': 'idea for a tune' }}
                                        onChange={handleInputKeyChange}
                                    />
                                </Paper> */}
                                <h1 className="text-4xl text-black mt-10">Orchestrate Generative Music</h1>

                                <div className="shadow-lg bg-white text-black text-left rounded-md mx-10 my-5">
                                    <Paper 
                                        style={{maxHeight: 200, overflow: 'auto'}}
                                        className='px-4 py-4'>
                                        <h1 align="center">Welcome to Orchestrate!</h1>
                                        <br />
                                        <p>We're your AI-powered Jam Band Tool! 
                                        Orchestrate utilizes natural language processing to determine the music you would like it to generate. 
                                        You will interact with the tool by typing a request in English. 
                                        To generate a piece of music please type your prompt in the field below and then select "GENERATE". 
                                        <br />
                                        <br />
                                        Behind the scenes, Orchestrate looks for the following information in your prompt, 
                                        however, not all information is needed for the model to generate a unique piece of music. 
                                        We encourage you to play around with the tool to explore what happens when certain features are present or omitted:
                                        <br />
                                        <li>BPM - beats per minute (30 - 200)</li>
                                        <li>Audio Key (ex: C major, A minor, D major, etc)</li>
                                        <li>Time Signature (ex: 4/4, 3/4, 6/8, 12/8)</li>
                                        <li>Pitch Range (ex: very low, low, mid low, mid, mid high, high, very high)</li>
                                        <li>Number of Measures (ex: 4, 8, 16)</li>
                                        <li>Instrument (ex: piano, violin, bass, guitar, timpani, choir, sax)</li>
                                        <li>Genre (ex: classical, rock, funk, electronic)</li>
                                        <li>Min & Max Velocity - determines range of volume (40 - 127)</li>
                                        <li>Chords - a list of chords you would like to hear (ex: C, A, G, D)</li></p>
                                        <br />
                                        <h1 align="center">Sample Prompts to Try:</h1>
                                        <p>1. Play a 4 measure rock piano song in the key of G.</p>
                                        <br />
                                        <p>2. I want to hear a 4 measure classical guitar accompaniment in the key of D major, 4/4 time signature, 100 BPM.</p>
                                        <br />
                                        <p>3. Can you give me a funky bass track in 3/4 time? 
                                        I want the piece to be 80 BPM, 4 measures, 
                                        in the key of A minor with the chords ["Am", "F", "D", "E"] and a mid low pitch range.
                                        </p>

                                    </Paper>
                            </div>
                                <Paper component="form" 
                                    className="flex justify-center h-35 w-200"
                                >
                                    <InputBase
                                        multiline
                                        fullWidth  
                                        sx={{ ml: 1, flex: 1 }}
                                        placeholder="Play a 4-measure accompaniment in the G minor key, using french horn. Keep the tempo at 235 BPM, with a 4/4 time signature..."
                                        rows={4}
                                        inputProps={{ 'aria-label': 'idea for a tune' }}
                                        onChange={handleInputChange}
                                    />
                                    <Button 
                                        className="my-4 mx-4" 
                                        component="label" 
                                        variant="contained" 
                                        startIcon={<Audiotrack/>}
                                        onClick={(e) => handleGenerationClick(e)}>
                                        Generate
                                    </Button>
                                </Paper>
                                <h1 className="text-2l text-black">Please email iy3827@berkeley.edu for technical support</h1>

                                {/* <h5 className="text-2l text-black">You have {files.length} to fuse</h5> */}
                                <div className="flex justify-center px-2 pt-4 pb-4">
                                    {/** Only render MIDI file when there is MIDI to render */}
                                    {/** Add a download button to download the midi file */}
                                    <MidiPlayer data={data} onStop={() => console.log(123)}/>
                                    { url === null?
                                        <Button className="mx-2" variant="contained" disabled>Disabled</Button> :
                                        <Button className="mx-2" variant="contained" color="primary" href={url} download>Download MIDI</Button> 
                                    }
                                    {progress ? <CircularProgress className="mx-2"/> : null}                          
                                </div>
                                <div className="flex justify-center px-2 pt-4 pb-4">
                                    { url === null?
                                        <Button className="mx-2" variant="contained" disabled>Disabled</Button> :
                                        <Button className="mx-2" 
                                            variant="contained" 
                                            color="primary"
                                            onClick={(e) => (convertToWav(e))}>
                                            Convert to Wav
                                        </Button>                                    
                                    }
                                    { wavUrl === null?
                                        <Button className="mx-2" variant="contained" disabled>Disabled</Button> :
                                        <Button className="mx-2" variant="contained" color="primary" href={wavUrl} download>Download Wav</Button>
                                    }
                                    {progress ? <CircularProgress className="mx-2"/> : null}                          
                                </div>
                            </div>
                        </div>
                          
                    </Slide>
                    <Slide direction="down" in={true} timeout={1000}>
                        <div className="shadow-lg bg-neutral-300 rounded-md px-20 pt-6 pb-8 mx-20">
                            <h1 className="text-4xl text-black mb-10">Audio Synthesizer</h1>
                                <Paper className="mx-40">
                                    <h1>Good Luck! Have Fun!</h1>
                                    <br />
                                    <p>Click to play your newly generated track on a continuous loop. Feel free to mix the track as you please!</p>
                                </Paper>
                                <Synthesizer progress={progress} bpm={tempo} steps={steps} midi={blobFile}/>
                        </div>
                    </Slide>
                    <br />
                    <div className="shadow-lg bg-white rounded-md mx-60 mt-2">
                        <Paper>
                            <h1 className="text-3xl text-black">Licenses & User Agreements</h1>
                            <br />
                            <h1 className="text-2xl">ComMU License</h1>
                            <a href="https://github.com/jeffreyjohnens/MetaMIDIDataset#copyright">ComMU Github</a>
                            <br/>
                            <a href="https://pozalabs.github.io/ComMU/">ComMU Demo</a>
                            <br />
                            <p>
                            The ComMU dataset is released under the Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License (CC BY-NC-SA 4.0). 
                            It is provided primarily for research purposes and is prohibited for commercial use.
                            </p>
                            <br />
                            <h1 className="text-2xl">MetaMIDI Copyright</h1>
                            <a href="https://github.com/jeffreyjohnens/MetaMIDIDataset#copyright">MetaMIDI Dataset Github</a>
                            <br/>
                            <a href="https://zenodo.org/records/5142664">MetaMIDI Dataset</a>
                            <p>
                            Since we did not transcribe any of the MIDI files in the MetaMIDI Dataset, 
                            we provide a list of the Copyright meta-events in the dataset to acknowledge the original authors of the files.
                            </p>
                        </Paper>
                    </div>
                </div>
            </div>
        </section>
    );
}

export default App;
