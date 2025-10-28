# Fisheries Catch Distribution Website

A web application for easy retrieval of historical fisheries catches and biological attributes from geographic results.

## Features

- **Geographic Search**: Search for fisheries catches by latitude, longitude, and radius
- **Interactive Map**: Visual representation of catch locations using Leaflet maps
- **Species Filter**: Filter catches by species name (scientific or common name)
- **Temporal Filter**: Filter catches by year
- **Biological Attributes**: View detailed biological information for each species including:
  - Maximum length and weight
  - Trophic level
  - Habitat type
  - Depth and temperature ranges
- **Statistics Dashboard**: Overview of total catches, weight, species, and regions

## Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/jimianelli/fishdistrib.git
cd fishdistrib
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

4. Open your web browser and navigate to:
```
http://localhost:5000
```

## Usage

### Searching for Catches

1. **Geographic Search**:
   - Click on the map to set coordinates, or manually enter latitude and longitude
   - Set a search radius in kilometers (default: 100 km)
   
2. **Filter by Species**:
   - Enter a species name (scientific or common name) in the Species field
   - Examples: "Cod", "Gadus morhua", "Tuna"

3. **Filter by Year**:
   - Select a specific year from the dropdown menu
   - Or leave it as "All Years" to see all available data

4. **View Results**:
   - Click the "Search" button to retrieve matching catches
   - Results will appear below and as markers on the map
   - Each result shows catch details and biological attributes

### Understanding the Results

Each catch record displays:
- **Species Information**: Scientific and common names
- **Catch Details**: Weight (kg) and year
- **Location**: Latitude, longitude, and region
- **Fishing Details**: Vessel type and fishing method
- **Biological Attributes**: Maximum size, trophic level, habitat, depth range, and temperature range

## Database Schema

### Catches Table
- `id`: Unique identifier
- `species`: Scientific species name
- `common_name`: Common species name
- `catch_weight`: Weight in kilograms
- `catch_year`: Year of catch
- `latitude`: Geographic latitude
- `longitude`: Geographic longitude
- `region`: Geographic region name
- `vessel_type`: Type of fishing vessel
- `fishing_method`: Method used for fishing

### Biological Attributes Table
- `id`: Unique identifier
- `species`: Scientific species name
- `common_name`: Common species name
- `max_length`: Maximum recorded length (cm)
- `max_weight`: Maximum recorded weight (kg)
- `trophic_level`: Position in food chain
- `habitat`: Primary habitat type
- `depth_range`: Depth range in meters
- `temperature_range`: Preferred temperature range

## API Endpoints

- `GET /api/search`: Search catches with query parameters (lat, lon, radius, species, year)
- `GET /api/species`: Get list of all species
- `GET /api/years`: Get list of all years with data
- `GET /api/regions`: Get list of all regions
- `GET /api/stats`: Get overall statistics

## Sample Data

The application includes sample data for demonstration purposes:
- 8 catch records from various species
- 7 species with biological attributes
- Data from 2020-2021 in North Atlantic and Gulf of Mexico regions

## Technology Stack

- **Backend**: Python Flask
- **Database**: SQLite
- **Frontend**: HTML5, CSS3, JavaScript
- **Mapping**: Leaflet.js with OpenStreetMap tiles

## License

See LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.