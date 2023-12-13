// react
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './components/App';

// import TestHiddenPage from './components/TestHiddenPage';
// import Synthesia from './components/DAW/Synthesia';
// import Synthesizer from './components/DAW/Synthesizer';
// import PlayMIDI from './components/PlayMIDI';

// tailwindcss
import './css/tailwind.css';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);