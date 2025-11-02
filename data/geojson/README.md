# GeoJSON Data Files

This directory contains geographic boundary data in GeoJSON format.

## Files

### baltic_border_union.geojson
Union of Baltic Sea border countries for mission visualization.

### baltic_sea_extracted.geojson
Extracted boundaries of Baltic Sea region.

### ne_110m_admin_0_countries.geojson
Natural Earth country boundaries (1:110m scale).
- Global country polygons for mapping
- Source: Natural Earth Data

## Usage

These files are used by:
- Map generation scripts in `maps/`
- Geometry utilities in `utils/map_making/`

## Data Sources

- Natural Earth: https://www.naturalearthdata.com/
- Custom extractions from mission data processing

## Format

All files follow GeoJSON specification (RFC 7946):
- Coordinates in WGS84 (EPSG:4326)
- Polygon/MultiPolygon geometries
- Properties include country names, codes, etc.
