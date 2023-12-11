
let map; 

function searchPlaces() {
    const keyword = document.getElementById('keyword').value;

    // Check if a keyword is entered
    if (!keyword) {
        alert('Please enter a keyword');
        return;
    }

    // Define the bounding box for Sri Lanka
    const boundingBox = '79.521,5.9255,81.879,9.9697';

    // Nominatam API
    const apiUrl = `https://nominatim.openstreetmap.org/search?q=${keyword}&format=json&bounded=1&viewbox=${boundingBox}`;

    // Fetch data from the API
    fetch(apiUrl)
        .then(response => response.json())
        .then(data => {
            displayResults(data);
            showLocationsOnMap(data);
        })
        .catch(error => console.error('Error fetching data:', error));
}

function displayResults(data) {
    const resultsContainer = document.getElementById('results');
    resultsContainer.innerHTML = ''; // Clear previous results

    if (data.length > 0) {
        // Display each result in the results container
        data.forEach(result => {
            const placeName = result.display_name;
            const placeType = result.type;
            const lat = result.lat;
            const lon = result.lon;

            // Create a result card
            const resultCard = document.createElement('div');
            resultCard.classList.add('result-card');
            resultCard.innerHTML = `
                <strong>${placeName}</strong><br>
                Type: ${placeType}<br>
                Latitude: ${lat}<br>
                Longitude: ${lon}
            `;

            resultsContainer.appendChild(resultCard);
        });
    } else {
        // Display a message if no results are found
        resultsContainer.innerHTML = '<p>No results found. Please try a different keyword.</p>';
    }
}

function showLocationsOnMap(data) {
    // Initialize the map centered at the first result's location
    const firstResult = data[0];
    const mapCenter = [parseFloat(firstResult.lat), parseFloat(firstResult.lon)];

    if (!map) {
        // Create a new map if it doesn't exist
        map = L.map('map').setView(mapCenter, 10);

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(map);
    }

    // Add markers for each result to the map
    data.forEach(result => {
        const marker = L.marker([parseFloat(result.lat), parseFloat(result.lon)])
            .bindPopup(result.display_name)
            .addTo(map);
    });

    // Fit the map to contain all markers
    const bounds = L.latLngBounds(data.map(result => [parseFloat(result.lat), parseFloat(result.lon)]));
    map.fitBounds(bounds);
}
