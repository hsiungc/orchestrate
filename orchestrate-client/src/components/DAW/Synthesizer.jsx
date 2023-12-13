import React, { useState } from 'react'
import { Song, Track, Instrument, Effect } from 'reactronica';
import { Donut } from 'react-dial-knob'
import { Button, CircularProgress, Stack, FormControl, FormLabel, FormControlLabel, Radio, RadioGroup } from '@mui/material';
import PlayCircleIcon from '@mui/icons-material/PlayCircle';
import PauseCircleIcon from '@mui/icons-material/PauseCircle';

const Synthesizer = (props) => {
    /* Declare state variables */
    const [isPlaying, setIsPlaying] = React.useState(false);
    const [volume, setVolume] = useState(-4);
    const [delayAmount, setDelayAmount] = useState(0);
    const [distortionAmount, setDistortion] = useState(0);
    const [reverbAmount, setReverbAmount] = useState(0);
    const [autoFilterAmount, setAutoFilterAmount] = useState(0);
    const [tremoloAmount, setTremoloAmount] = useState(0);
    const [oscillatorType, setOscillatorType] = useState('sine');
    const [synthType, setSynthType] = useState('fmSynth');

    // loading url state
    const [url, setUrl] = useState(null);
    const [progress, setProgress] = useState(false);



    const parseSynthFile = async (e) => {
        e.preventDefault();
        setProgress(true);
        try {
            // convert files to form data
            // create a form data object to send to the server api
            // the form data object will contain the midi file
            const file = new File([props.midi], 'output.mid', { type: 'audio/midi' });
            const formData = new FormData();
            formData.append('midiFile', file);
            formData.append('synthType', synthType);
            formData.append('oscillatorType', oscillatorType);
            formData.append('volume', (1 - (50-4+volume)/(50-4)).toFixed(2));
            formData.append('delay', delayAmount);
            formData.append('distortion', distortionAmount*100);
            formData.append('reverb', reverbAmount*100);
            formData.append('autoFilter', autoFilterAmount*100);
            formData.append('tremolo', tremoloAmount*100);

            console.log( (1 - (50-4+volume)/(50-4)).toFixed(2));


            // build the post data to be sent to the server api
            const postData = {
                method:'POST',
                body: formData
            };
            // initiate fetch request on the server api
            // const response = await fetch('/api/applysynth', postData);
            const response = await fetch('https://api.orchestrate-api-server.com/api/applysynth', postData);


            if (response.status === 200){
                //Begin parsing the response for immediate playback
                const blob = await response.blob();

                // create a url from blob to be use for download
                const midiFileDownload = window.URL.createObjectURL(blob);
                setUrl(midiFileDownload);

            }
        } catch (error) {
            alert("Error "+ error);

        }
        setProgress(false);

    }

    return (
        <div className="container-fluid pt-2 py-2">
            <div className="flex justify-center mt-4 mb-4">
                {
                    props.steps.length === 0 ? 
                    <Button className="mb-2 mx-2" variant="contained" disabled>Disabled</Button>
                    :
                    <Button className="mb-2 mx-2" 
                        variant="contained" 
                        color="primary"
                        startIcon={isPlaying ? <PauseCircleIcon/> : <PlayCircleIcon />}
                        onClick={() => {
                            setIsPlaying(!isPlaying);
                        }}
                    >{isPlaying ? 'Stop' : 'Play'}
                    </Button>
                }                
                
                {props.progress ? <CircularProgress className="mx-2"/> : null}                          

                {isPlaying ? 
                <Song isPlaying={isPlaying} bpm={props.bpm}>
                    <Track
                        steps={props.steps}
                        volume={volume}

                        // Callback for every step
                        onStepPlay={(step, index) => {
                            console.log(step, index);
                        }}
                    >
                    <Instrument type={synthType} oscillator={oscillatorType}/>

                    {/* Setup the effect chain */}
                    <Effect type="tremolo" wet={tremoloAmount} />
                    <Effect type="distortion" wet={distortionAmount} />
                    <Effect type="freeverb" wet={reverbAmount} />
                    <Effect type="feedbackDelay" wet={delayAmount} />
                    <Effect type="autoFilter" wet={autoFilterAmount} />
                    </Track>
                </Song> : null}
            </div>

            <div className="flex justify-center text-black">
                {
                    props.steps.length === 0 ? 
                    <Button className="mb-2 mx-2" variant="contained" disabled>Disabled</Button>:
                    <Button className="mb-2 mx-2" 
                        variant="contained" 
                        color="primary"
                        onClick={(e) => (parseSynthFile(e))}>
                        Finalize
                    </Button>
                }
                { url === null?
                    <Button className="mb-2 mx-2" variant="contained" disabled>Disabled</Button> :
                    <Button className="mb-2 mx-2" 
                        variant="contained" 
                        color="primary"
                        href={url}
                        download>Download Synth
                    </Button>          
                }
                {progress ? <CircularProgress className="mx-2"/> : null}                          
            </div>


            <div className="flex justify-center text-black">
                {/** Create Some Dial Knobs **/}
                <Stack spacing={2} direction="row" sx={{ mb: 1 }} alignItems="center" className='CenterAlign'>
                    <Donut
                        diameter={100}
                        min={0}
                        max={1}
                        step={.25}
                        value={tremoloAmount}
                        theme={{
                            donutColor: 'black',
                            donutThickness: 14
                        }}
                        onValueChange={setTremoloAmount}
                        ariaLabelledBy={'tremolo-amount'}
                        >
                        <label id={'tremolo-amount'}>Tremolo</label>
                    </Donut>

                    <Donut
                        diameter={100}
                        min={0}
                        max={1}
                        step={.25}
                        value={distortionAmount}
                        theme={{
                            donutColor: 'black',
                            donutThickness: 14
                        }}
                        onValueChange={setDistortion}
                        ariaLabelledBy={'delay-amount'}
                    >
                    <label id={'delay-amount'}>Distortion</label>
                    </Donut>

                    <Donut
                        diameter={100}
                        min={0}
                        max={1}
                        step={.25}
                        value={reverbAmount}
                        theme={{
                            donutColor: 'black',
                            donutThickness: 14
                        }}
                        onValueChange={setReverbAmount}
                        ariaLabelledBy={'reverb'}
                        >
                        <label id={'reverb'}>Reverb</label>
                    </Donut>
                </Stack>
            </div>
            <div className="flex justify-center text-black">
                <Stack spacing={2} direction="row" sx={{ mb: 1 }} alignItems="center" className='CenterAlign'>
                    <Donut
                        diameter={100}
                        min={0}
                        max={1}
                        step={.25}
                        value={delayAmount}
                        theme={{
                            donutColor: 'black',
                            donutThickness: 14
                        }}
                        onValueChange={setDelayAmount}
                        ariaLabelledBy={'delay-amount'}
                        >
                        <label id={'delay-amount'}>Delay</label>
                    </Donut>

                    <Donut
                        diameter={100}
                        min={0}
                        max={1}
                        step={.25}
                        value={autoFilterAmount}
                        theme={{
                            donutColor: 'black',
                            donutThickness: 14
                        }}
                        onValueChange={setAutoFilterAmount}
                        ariaLabelledBy={'delay-amount'}
                        >
                        <label id={'delay-amount'}>AutoFilter</label>
                    </Donut>

                    <Donut
                        diameter={100}
                        min={-50}
                        max={10}
                        step={1}
                        value={volume}
                        theme={{
                            donutColor: 'black',
                            donutThickness: 14
                        }}
                        onValueChange={setVolume}
                        ariaLabelledBy={'volume'}
                        >
                        <label id={'volume'}>Volume</label>
                    </Donut>
                </Stack>
            </div>
            <br />
            <div className="flex justify-center text-black">
                <Stack spacing={2} direction="row" sx={{ mb: 1 }} alignItems="center" className='CenterAlign'>
                    <FormControl component="fieldset">
                    <FormLabel component="legend"><b>Synth Engine</b></FormLabel>
                    <RadioGroup
                        aria-label="synth-engine"
                        defaultValue="duoSynth"
                        name="radio-buttons-group"
                    >
                        <FormControlLabel value="amSynth" control={<Radio onClick={() => setSynthType('amSynth')} />} label="amSynth" />
                        <FormControlLabel value="fmSynth" control={<Radio onClick={() => setSynthType('fmSynth')} />} label="fmSynth" />
                        <FormControlLabel value="duoSynth" control={<Radio onClick={() => setSynthType('duoSynth')} />} label="duoSynth" />
                    </RadioGroup>
                    </FormControl>

                    <FormControl component="fieldset">
                    <FormLabel component="legend"><b>Oscillator Type</b></FormLabel>
                    <RadioGroup
                        aria-label="synth-engine"
                        defaultValue="triangle"
                        name="radio-buttons-group"
                    >
                        <FormControlLabel value="sine" control={<Radio onClick={() => setOscillatorType('sine')} />} label="Sine" />
                        <FormControlLabel value="triangle" control={<Radio onClick={() => setOscillatorType('triangle')} />} label="Triangle" />
                        <FormControlLabel value="square" control={<Radio onClick={() => setOscillatorType('square')} />} label="Square" />
                    </RadioGroup>
                    </FormControl>
                </Stack>
            </div>
        </div>
    );

}

export default Synthesizer;