import React from 'react';
import { Midi } from '@tonejs/midi';

const MIDIParser = () => {
  const [steps, setSteps] = React.useState([]);

  const handleMidiFileChange = async (event) => {
    const file = event.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = async (e) => {
        const midiData = e.target.result;
        const midi = new Midi(midiData);
        const extractedSteps = extractStepsFromMidi(midi);
        setSteps(extractedSteps);
      };
      reader.readAsArrayBuffer(file);
    }
  };

  const extractStepsFromMidi = (midi) => {
    const steps = [];
    midi.tracks.forEach((track) => {
      track.notes.forEach((note) => {
        steps.push({
          note: note.name,
          duration: note.duration,
          time: note.midi,
        });
      });
    });
    console.log(steps)
    return steps;
  };

  return (
    <div>
      <input type="file" accept=".mid" onChange={handleMidiFileChange} />
      <div>
        <h2>Extracted Steps</h2>
        <ul>
          {steps.map((step, index) => (
            <li key={index}>{`Note: ${step.note}, Duration: ${step.duration}, Time: ${step.time}`}</li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default MIDIParser;