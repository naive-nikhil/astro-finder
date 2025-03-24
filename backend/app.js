require('dotenv').config();

// Import required modules
const express = require('express');
const { spawn } = require('child_process');
const axios = require('axios');
const app = express();
const port = process.env.PORT || 3000;
const path = require('path');

const OPENCAGE_API_KEY = 'cd1a1102e21c48b6b20b80ecc2e7ed61'; // Replace with your API key
const TIMEZONEDB_API_KEY = '7W24C04UTE0P'; // Replace with your API key

// Middleware to parse JSON bodies
app.use(express.json());

app.get("/", (req, res)=>{
  res.send("Server Running API Status - Live");
})

// Keep the original GET endpoint
app.get('/hello', (req, res) => {
  const name = req.query.name || 'Guest';
  res.json({
    message: `Hello, ${name}!`
  });
});


// Endpoint that processes data through Python script
app.post('/api/process', async (req, res) => {
  // Extract parameters from the request body
  const { date, time, place } = req.body;

  try {
    
    if (!place) {
      return res.status(400).json({ error: 'Please provide a place name using the "place" query parameter' });
    }
    
    // Step 1: Get coordinates from OpenCage Geocoder
    const geocodeResponse = await axios.get('https://api.opencagedata.com/geocode/v1/json', {
      params: {
        q: place,
        key: OPENCAGE_API_KEY,
        limit: 1
      }
    });
    
    // Check if we got any results
    if (geocodeResponse.data.results.length === 0) {
      return res.status(404).json({ error: 'Place not found' });
    }
    
    // Extract coordinates and formatted location
    const location = geocodeResponse.data.results[0];
    const { lat, lng } = location.geometry;
    const formattedAddress = location.formatted;

    
    // Step 2: Get timezone from TimeZoneDB
    const timezoneResponse = await axios.get('http://api.timezonedb.com/v2.1/get-time-zone', {
      params: {
        key: TIMEZONEDB_API_KEY,
        format: 'json',
        by: 'position',
        lat: lat,
        lng: lng
      }
    });
    
    // Combine the data and send the response
    const result = {
      place: formattedAddress,
      coordinates: {
        latitude: lat,
        longitude: lng
      },
      timezone: {
        zoneName: timezoneResponse.data.zoneName,
      }
    };

      // Create data object to send to Python
  const dataToProcess = {
    date: date || null,
    time: time || null,
    lat: lat || null,
    lng: lng || null,
    timezone: timezoneResponse.data.zoneName || null,
  };
  
  // Spawn Python process
  const pythonProcess = spawn('python3', [path.join(__dirname, 'process_data.py')]);
  
  let pythonData = '';
  let pythonError = '';
  
  // Send data to Python script via stdin
  pythonProcess.stdin.write(JSON.stringify(dataToProcess));
  pythonProcess.stdin.end();
  
  // Collect data from Python script
  pythonProcess.stdout.on('data', (data) => {
    pythonData += data.toString();
  });
  
  // Collect any errors from Python script
  pythonProcess.stderr.on('data', (data) => {
    pythonError += data.toString();
  });
  
  // When Python script finishes
  pythonProcess.on('close', (code) => {
    if (code !== 0) {
      // If Python script had an error
      return res.status(500).json({
        error: 'Python processing failed',
        details: pythonError
      });
    }
    
    try {
      // Parse the Python output as JSON
      const processedData = JSON.parse(pythonData);
      res.json(processedData);
    } catch (error) {
      res.status(500).json({ 
        error: 'Failed to parse Python output', 
        details: error.message,
        pythonOutput: pythonData
      });
    }
  });
    
  } catch (error) {
    console.error('Error:', error.message);
    res.status(500).json({ 
      error: 'An error occurred while processing your request',
      details: error.message
    });
  }
});

// Start the server
app.listen(port, () => {
  console.log(`Server is running on http://localhost:${port}`);
});