import React from 'react';
import './App.css';
import RequestForm from './RequestForm';

function App() {
    return (
        <div className="App">
            <header className="App-header">
                <h1>Request for Weekly Covid Updates</h1>
                <RequestForm />
            </header>
        </div>
    );
}

export default App;
