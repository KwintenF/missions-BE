#!/usr/bin/env python3
"""
Extract geographical data from the c-globe-spin-container on mil.be/nl/onze-missies/

OUTPUT: data/globe_locations.json
"""
import re
import json
import requests
from bs4 import BeautifulSoup


def extract_globe_locations(url="https://www.mil.be/nl/onze-missies/"):
    """Extract the globeLocations array from the page."""

    response = requests.get(url)
    response.raise_for_status()
    text = response.text

    # Find where globeLocations starts
    start_match = re.search(r'window\.globeLocations\s*=\s*', text)
    if not start_match:
        return None

    start_pos = start_match.end()

    # Extract the array by counting brackets
    depth = 0
    in_array = False
    end_pos = start_pos

    for i in range(start_pos, len(text)):
        char = text[i]
        if char == '[':
            depth += 1
            in_array = True
        elif char == ']':
            depth -= 1
            if depth == 0 and in_array:
                end_pos = i + 1
                break

    json_str = text[start_pos:end_pos]

    try:
        locations_data = json.loads(json_str)
        return locations_data
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return None


if __name__ == "__main__":
    print("Extracting globe location data from mil.be...")

    locations = extract_globe_locations()

    if locations:
        print(f"\nFound {len(locations)} locations:")
        print(json.dumps(locations, indent=2, ensure_ascii=False))

        # Save to file
        with open('data/globe_locations.json', 'w', encoding='utf-8') as f:
            json.dump(locations, f, indent=2, ensure_ascii=False)
        print(f"\nData saved to data/globe_locations.json")
    else:
        print("Could not extract globe locations")
