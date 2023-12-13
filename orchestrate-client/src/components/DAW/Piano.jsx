import React from 'react';

const Piano = ({ activeNotes }) => {
  const octaves = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']; // All notes in an octave

//   console.log(activeNotes);

  return (
    <div className="piano">
      {octaves.map((note, index) => (
        <div key={index} className={`key ${activeNotes.includes(note) ? 'active' : ''}`}>
          {note}
        </div>
      ))}
    </div>
  );
};

export default Piano;