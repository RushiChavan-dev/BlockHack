import React, { useState } from 'react';

const requestsData = {
    covid: {
        2020: 100,
        2021: 200,
        2022: 300
    },
    flu: {
        2020: 150,
        2021: 180,
        2022: 160
    }
    // Add more diseases and request data as needed
};

const RequestForm = () => {
    const [disease, setDisease] = useState('');
    const [year, setYear] = useState('');
    const [result, setResult] = useState('');

    const handleSubmit = (e) => {
        e.preventDefault();
        if (requestsData[disease] && requestsData[disease][year]) {
            const numRequests = requestsData[disease][year];
            setResult(`Number of requests for ${disease} in ${year}: ${numRequests}`);
        } else {
            setResult(`No data available for ${disease} in ${year}`);
        }
    };

    return (
        <div>
            <form onSubmit={handleSubmit}>
                <div>
                    <label htmlFor="disease">Disease:</label>
                    <select 
                        id="disease" 
                        value={disease} 
                        onChange={(e) => setDisease(e.target.value)}
                    >
                        <option value="">Select Region</option>
                        <option value="toronto">Toronto</option>
                        <option value="ottawa">Ottawa</option>
                        {/* Add more options as needed */}
                    </select>
                </div>
                <div>
                    <label htmlFor="year">Week:</label>
                    <input 
                        type="text" 
                        id="year" 
                        value={year} 
                        onChange={(e) => setYear(e.target.value)} 
                        placeholder="Enter Week ...."
                    />
                </div>
                <button type="submit">Submit</button>
            </form>
            {result && <div>{result}</div>}
        </div>
    );
};

export default RequestForm;
