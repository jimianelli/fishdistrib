// Initialize map
let map;
let markers = [];

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Leaflet map (if Leaflet is available)
    if (typeof L !== 'undefined') {
        try {
            map = L.map('map').setView([55.0, -3.0], 4);
            
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '© OpenStreetMap contributors',
                maxZoom: 19
            }).addTo(map);
            
            // Map click event to set coordinates
            map.on('click', function(e) {
                document.getElementById('latitude').value = e.latlng.lat.toFixed(3);
                document.getElementById('longitude').value = e.latlng.lng.toFixed(3);
            });
        } catch (error) {
            console.error('Error initializing map:', error);
            document.getElementById('map').innerHTML = '<p style="padding: 20px; text-align: center; color: #999;">Map unavailable. You can still search using coordinates.</p>';
        }
    } else {
        document.getElementById('map').innerHTML = '<p style="padding: 20px; text-align: center; color: #999;">Map library not loaded. You can still search using coordinates.</p>';
    }
    
    // Load initial data
    loadStats();
    loadYears();
    
    // Set up event listeners
    document.getElementById('search-form').addEventListener('submit', handleSearch);
    document.getElementById('reset-btn').addEventListener('click', handleReset);
});

async function loadStats() {
    try {
        const response = await fetch('/api/stats');
        const stats = await response.json();
        
        document.getElementById('total-catches').textContent = stats.total_catches || 0;
        document.getElementById('total-weight').textContent = 
            (stats.total_weight || 0).toLocaleString('en-US', {maximumFractionDigits: 1});
        document.getElementById('total-species').textContent = stats.total_species || 0;
        document.getElementById('total-regions').textContent = stats.total_regions || 0;
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

async function loadYears() {
    try {
        const response = await fetch('/api/years');
        const years = await response.json();
        
        const yearSelect = document.getElementById('year');
        years.forEach(year => {
            const option = document.createElement('option');
            option.value = year;
            option.textContent = year;
            yearSelect.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading years:', error);
    }
}

async function handleSearch(e) {
    e.preventDefault();
    
    const lat = document.getElementById('latitude').value;
    const lon = document.getElementById('longitude').value;
    const radius = document.getElementById('radius').value;
    const species = document.getElementById('species').value;
    const year = document.getElementById('year').value;
    
    const params = new URLSearchParams();
    if (lat) params.append('lat', lat);
    if (lon) params.append('lon', lon);
    if (radius) params.append('radius', radius);
    if (species) params.append('species', species);
    if (year) params.append('year', year);
    
    try {
        const response = await fetch(`/api/search?${params}`);
        const results = await response.json();
        
        displayResults(results);
        displayMarkersOnMap(results);
    } catch (error) {
        console.error('Error searching:', error);
        alert('Error searching data. Please try again.');
    }
}

function handleReset() {
    document.getElementById('search-form').reset();
    document.getElementById('results-container').innerHTML = 
        '<p class="no-results">Enter search criteria and click Search to view results.</p>';
    document.getElementById('count').textContent = '0';
    clearMarkers();
}

function displayResults(results) {
    const container = document.getElementById('results-container');
    const countElement = document.getElementById('count');
    
    countElement.textContent = results.length;
    
    if (results.length === 0) {
        container.innerHTML = '<p class="no-results">No catches found matching your criteria.</p>';
        return;
    }
    
    container.innerHTML = results.map(result => `
        <div class="result-card">
            <div class="result-header">
                <div class="species-info">
                    <h3>${result.common_name || result.species}</h3>
                    <p>${result.species}</p>
                </div>
                <div class="catch-info">
                    <div class="catch-weight">${result.catch_weight.toFixed(1)} kg</div>
                    <div class="catch-year">${result.catch_year}</div>
                </div>
            </div>
            
            <div class="result-details">
                <div class="detail-group">
                    <span class="detail-label">Location</span>
                    <span class="detail-value">${result.latitude.toFixed(2)}°, ${result.longitude.toFixed(2)}°</span>
                </div>
                <div class="detail-group">
                    <span class="detail-label">Region</span>
                    <span class="detail-value">${result.region || 'N/A'}</span>
                </div>
                <div class="detail-group">
                    <span class="detail-label">Vessel Type</span>
                    <span class="detail-value">${result.vessel_type || 'N/A'}</span>
                </div>
                <div class="detail-group">
                    <span class="detail-label">Fishing Method</span>
                    <span class="detail-value">${result.fishing_method || 'N/A'}</span>
                </div>
            </div>
            
            ${result.biological && result.biological.habitat ? `
            <div class="biological-section">
                <h4>Biological Attributes</h4>
                <div class="biological-attributes">
                    ${result.biological.max_length ? `
                    <div class="detail-group">
                        <span class="detail-label">Max Length</span>
                        <span class="detail-value">${result.biological.max_length} cm</span>
                    </div>` : ''}
                    ${result.biological.max_weight ? `
                    <div class="detail-group">
                        <span class="detail-label">Max Weight</span>
                        <span class="detail-value">${result.biological.max_weight} kg</span>
                    </div>` : ''}
                    ${result.biological.trophic_level ? `
                    <div class="detail-group">
                        <span class="detail-label">Trophic Level</span>
                        <span class="detail-value">${result.biological.trophic_level}</span>
                    </div>` : ''}
                    ${result.biological.habitat ? `
                    <div class="detail-group">
                        <span class="detail-label">Habitat</span>
                        <span class="detail-value">${result.biological.habitat}</span>
                    </div>` : ''}
                    ${result.biological.depth_range ? `
                    <div class="detail-group">
                        <span class="detail-label">Depth Range</span>
                        <span class="detail-value">${result.biological.depth_range}</span>
                    </div>` : ''}
                    ${result.biological.temperature_range ? `
                    <div class="detail-group">
                        <span class="detail-label">Temperature</span>
                        <span class="detail-value">${result.biological.temperature_range}</span>
                    </div>` : ''}
                </div>
            </div>` : ''}
        </div>
    `).join('');
}

function displayMarkersOnMap(results) {
    // Only display markers if map is available
    if (!map || typeof L === 'undefined') {
        return;
    }
    
    clearMarkers();
    
    if (results.length === 0) return;
    
    const bounds = [];
    
    results.forEach(result => {
        const marker = L.marker([result.latitude, result.longitude])
            .addTo(map)
            .bindPopup(`
                <strong>${result.common_name || result.species}</strong><br>
                Weight: ${result.catch_weight.toFixed(1)} kg<br>
                Year: ${result.catch_year}<br>
                Region: ${result.region || 'N/A'}
            `);
        
        markers.push(marker);
        bounds.push([result.latitude, result.longitude]);
    });
    
    if (bounds.length > 0) {
        map.fitBounds(bounds, { padding: [50, 50] });
    }
}

function clearMarkers() {
    if (map && typeof L !== 'undefined') {
        markers.forEach(marker => map.removeLayer(marker));
    }
    markers = [];
}
