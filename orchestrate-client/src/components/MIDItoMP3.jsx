mport React, { useState } from 'react';
import { Midi } from '@tonejs/midi';
import lamejs from 'lamejs';

const MidiToMp3Converter = () => {
  const [midiFile, setMidiFile] = useState(null);

  const handleMidiInputChange = (event) => {
    const file = event.target.files[0];
    setMidiFile(file);
  };

  const convertMidiToMp3 = async () => {
    if (!midiFile) {
      console.error('Please select a MIDI file.');
      return;
    }

    const reader = new FileReader();

    reader.onload = async (event) => {
      const midiArrayBuffer = event.target.result;
      const midi = new Midi(midiArrayBuffer);

      // You can use tone.js to play the MIDI file
      // For simplicity, we'll just log the MIDI data here
      console.log('MIDI Data:', midi);

      // Convert MIDI to PCM audio using tone.js
      const audioBuffer = await midi.toWav();

      // Convert PCM audio to MP3 using lamejs
      const mp3Encoder = new lamejs.Mp3Encoder(1, audioBuffer.sampleRate, 128);
      const samples = audioBuffer.getChannelData(0);
      const sampleBlockSize = 1152; // Must be a multiple of 576
      const mp3Data = [];
      for (let i = 0; i < samples.length; i += sampleBlockSize) {
        const sampleBlock = samples.subarray(i, i + sampleBlockSize);
        const mp3Block = mp3Encoder.encodeBuffer(sampleBlock);
        if (mp3Block.length > 0) {
          mp3Data.push(new Int8Array(mp3Block));
        }
      }

      const mp3Blob = new Blob(mp3Data, { type: 'audio/mp3' });
      const mp3Url = URL.createObjectURL(mp3Blob);
      window.open(mp3Url, '_blank');
    };

    reader.readAsArrayBuffer(midiFile);
  };

  return (
    <div>
      <input type="file" accept=".midi, .mid" onChange={handleMidiInputChange} />
      <button onClick={convertMidiToMp3}>Convert to MP3</button>
    </div>
  );
};

export default MidiToMp3Converter;