import React, { useState, useEffect } from 'react';
import { Midi } from '@tonejs/midi';
import Piano from './Piano';
import * as Tone from 'tone';

const Synthesia = () => {
    const [midiData, setMidiData] = useState(null);
    const [activeNotes, setActiveNotes] = useState([]);
        
    useEffect(() => {
        parseMidi_v2(midiData);
    }, [midiData]);

    const handleMidiFileChange = async (event) => {
        const file = event.target.files[0];
        if (file) {
        const reader = new FileReader();
        reader.onload = async (e) => {
            setActiveNotes([]); // Clear active notes when a new MIDI file is loaded
            setMidiData(e.target.result);
        };
        reader.readAsArrayBuffer(file);
        }
    };


    const parseMidi_v2 = (midiData) => {
        if (midiData) {
            const midi = new Midi(midiData);
            const synth = new Tone.Synth().toDestination();
      
            const tempo = midi.header.tempos[0].bpm; // Get the tempo of the MIDI file
            Tone.Transport.bpm.value = tempo;
      
            midi.header.tempos.forEach((tempo) => {
                Tone.Transport.bpm.value = tempo.bpm;
            });
      
            midi.tracks.forEach((track) => {
                const startTime = 0;
                track.notes.forEach((note) => {
                    const { midi: midiNote, time, duration } = note;

                    // remove note active
                    const playingNotes = note.name.replace(/[0-9]/g, '')
        
                    // Calculate time in milliseconds based on the tempo and time in the MIDI file
                    const startTime = `+${(time * (60 / tempo))}`;
                    const endTime = `+${(time + duration) * (60 / tempo)}`;
        
                    // Schedule note start and end times
                    Tone.Transport.scheduleOnce((time) => {
                        synth.triggerAttack(Tone.Frequency(midiNote, 'midi'));
                        setActiveNotes((prevNotes) => [...prevNotes, playingNotes]);
                    }, startTime);
        
                    Tone.Transport.scheduleOnce((time) => {
                        synth.triggerRelease();
                        setActiveNotes((prevNotes) => prevNotes.filter((activeNote) => activeNote !== playingNotes));
                    }, endTime);
                });
            });
            Tone.Transport.start();
        }
        return () => {
            Tone.Transport.stop();
            Tone.Transport.cancel(); // Clear any scheduled Transport events
        };
    }

    return (
        <div className="synthesia-container">
            <input type="file" accept=".mid" onChange={handleMidiFileChange} />
            {midiData && <Piano activeNotes={activeNotes} />}
        </div>
    );
};

export default Synthesia;