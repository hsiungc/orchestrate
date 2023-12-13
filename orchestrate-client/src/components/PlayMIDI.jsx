import MidiPlayer from "react-midi-player";
import { useRef, useState } from "react";
import { parseArrayBuffer } from "midi-json-parser";
import { encode } from "json-midi-encoder";

function PlayMIDI() {
  const [url, setUrl] = useState("");
  const [fileMidi, setFileMidi] = useState(null);
  const [customMidiFile, setCustomMidiFile] = useState({
    replaySpeed: 1,
    key: 0
  });

  const onChangeSettingMidi = (event, field) => {
    setCustomMidiFile((p) => {
      const data = { ...p, [field]: +event.target.value };
      handleChangeMidiFile(fileMidi, data);
      return data;
    });
  };

  const transposeAmountOptions = [];
  for (let i = -6; i <= 5; i++) {
    transposeAmountOptions.push(
      <option key={i} value={i}>
        {i}
      </option>
    );
  }

  const playbackSpeedOptions = [];
  for (let i = 0.5; i <= 2; i += 0.25) {
    playbackSpeedOptions.push(
      <option key={i} value={i}>
        {i}
      </option>
    );
  }

  const handleChangeMidiFile = (fileMidi, { key, replaySpeed }) => {
    if (fileMidi) {
      const reader = new FileReader();
      

      reader.onload = async (event) => {
        parseArrayBuffer(event.target.result).then((json) => {
          json.tracks?.[0].map((event) => {
            if (event.noteOn || event.noteOff) {
              event.delta = Math.round(event.delta / replaySpeed);
              if (event.noteOn) {
                event.noteOn.noteNumber += key;
              } else {
                event.noteOff.noteNumber += key;
              }
            }

            return event;
          });

          encode(json).then((midiFile) => {
            const midiArray = new Uint8Array(midiFile);
            setUrl(midiArray);
          });
        });
      };
      reader.readAsArrayBuffer(fileMidi);
    }
  };

  const handleFileSelect = async (e) => {
    const file = e.target.files[0];
    console.log(file);
    handleChangeMidiFile(file, customMidiFile);
    setFileMidi(file);
  };

  return (
    <div className="App">
      <div
        className="App-header"
        style={{
          flexDirection: "column",
          justifyContent: "center",
          display: "flex"
        }}
      >
        <MidiPlayer data={url} onStop={() => console.log(123)} />
        <input type="file" onChange={handleFileSelect} accept="audio/midi" />
        Replay Speed
        <select
          value={customMidiFile.replaySpeed}
          onChange={(e) => onChangeSettingMidi(e, "replaySpeed")}
        >
          {playbackSpeedOptions}
        </select>
        Key
        <select
          value={customMidiFile.key}
          onChange={(e) => onChangeSettingMidi(e, "key")}
        >
          {transposeAmountOptions}
        </select>
      </div>
    </div>
  );
}

export default PlayMIDI;


const handleChangeMidiFile = (fileMidi, { key, replaySpeed }) => {
  if (fileMidi) {
      const reader = new FileReader();
      reader.onload = async (event) => {
          parseArrayBuffer(event.target.result).then((json) => {
              json.tracks?.[0].map((event) => {
                  if (event.noteOn || event.noteOff) {
                      event.delta = Math.round(event.delta / replaySpeed);
                      if (event.noteOn) {
                          event.noteOn.noteNumber += key;
                      } else {
                          event.noteOff.noteNumber += key;
                      }
                  }
                  return event;
              });

              // modify this for multiple tracks
              encode(json).then((midiFile) => {
                  console.log(json)
                  // encode MIDI file to Uint8Array
                  setData(""); // clear the data state
                  const midiArray = new Uint8Array(midiFile);
                  setData(midiArray);

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