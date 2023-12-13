import React, { useEffect, useState } from 'react';
import * as Tone from 'tone';
import { Midi } from '@tonejs/midi';

const MidiPlayer = () => {
  const [synth, setSynth] = useState(null);
  const [oscillatorType, setOscillatorType] = useState('sine');

  useEffect(() => {
    const initSynth = () => {
      // Create a Tone.js Synth with effects
      const newSynth = new Tone.Synth({
        oscillator: {
          type: oscillatorType // Adjust the synth type
        },
        envelope: {
          attack: 0.1,
          decay: 0.2,
          sustain: 0.3,
          release: 0.4
        }
      });

      // Apply effects
      const distortion = new Tone.Distortion(0.8); // Adjust the distortion level
      const volume = new Tone.Volume(-10); // Adjust the volume level
      const delay = new Tone.FeedbackDelay('8n', 0.5); // Adjust the delay time
      const reverb = new Tone.Reverb(1).toDestination();
      const autoFilter = new Tone.AutoFilter('4n').start();
      const tremolo = new Tone.Tremolo().start();

      // Connect effects
      newSynth.connect(distortion);
      distortion.connect(volume);
      volume.connect(delay);
      delay.connect(reverb);
      reverb.connect(autoFilter);
      autoFilter.connect(tremolo);
      tremolo.toDestination();

      setSynth(newSynth);
    };

    initSynth();

    // Cleanup function
    return () => {
      // Stop the Tone.js Transport when the component unmounts
      Tone.Transport.stop();
      Tone.Transport.cancel();
    };
  }, [oscillatorType]);

  useEffect(() => {
    if (synth) {
      // Update oscillator type when it changes
      synth.oscillator.type = oscillatorType;
    }
  }, [synth, oscillatorType]);

  const handleOscillatorChange = (newType) => {
    setOscillatorType(newType);
  };

  const playMidiWithEffects = async () => {
    // Load your MIDI file using @tonejs/midi
    const response = await fetch('path/to/your/midi/file.mid');
    const midiData = await response.arrayBuffer();
    const midi = new Midi(midiData);

    // Schedule MIDI events
    midi.tracks.forEach((track) => {
      track.notes.forEach((note) => {
        synth.triggerAttackRelease(note.name, note.duration, note.time, note.velocity);
      });
    });

    // Start Tone.js Transport to play the MIDI events
    Tone.Transport.start();
  };

  return (
    <div>
      <h1>MIDI Player with Effects</h1>
      <button onClick={playMidiWithEffects}>Play MIDI</button>
      <div>
        <label>Oscillator Type:</label>
        <select onChange={(e) => handleOscillatorChange(e.target.value)}>
          <option value="sine">Sine</option>
          <option value="square">Square</option>
          <option value="sawtooth">Sawtooth</option>
          <option value="triangle">Triangle</option>
        </select>
      </div>
      {/* You can add more UI elements or controls here if needed */}
    </div>
  );
};

export default MidiPlayer;