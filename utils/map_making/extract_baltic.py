#!/usr/bin/env python3
"""
Extract Baltic Sea polygon from the union of bordering countries.

Uses polygon closing method to create an accurate Baltic Sea representation
by connecting two points across the Danish straits.

OUTPUT: data/test-data/baltic_sea_extracted.geojson
"""
import json
import os
from .polygon_closing import close_polygon


def extract_baltic_sea(polygon, point1=None, point2=None):
    """
    Extract Baltic Sea polygon using polygon closing method.

    Creates a closed polygon by connecting two boundary points across
    the Danish straits (between Skagen and Göteborg).

    Args:
        polygon: List of [lon, lat] coordinates forming the union boundary
        point1: First closing point [lon, lat] (default: Skagen, Denmark)
        point2: Second closing point [lon, lat] (default: Göteborg, Sweden)

    Returns:
        List of [lon, lat] coordinates forming Baltic Sea polygon
    """
    # Default closing points across Danish straits
    if point1 is None:
        point1 = [10.6, 57.7]  # Near Skagen, Denmark
    if point2 is None:
        point2 = [11.9, 57.7]  # Near Göteborg, Sweden

    print(f"Extracting Baltic Sea using polygon closing method")
    print(f"Closing points:")
    print(f"  Point 1 (Skagen area): {point1}")
    print(f"  Point 2 (Göteborg area): {point2}")

    # Use polygon closing to extract Baltic
    baltic_polygon = close_polygon(polygon, point1, point2)

    return baltic_polygon


if __name__ == "__main__":
    # Get paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, '..', 'data')
    test_data_dir = os.path.join(data_dir, 'test-data')

    print("=" * 60)
    print("Baltic Sea Extraction using Polygon Closing Method")
    print("=" * 60)

    # Load the union data (from main data)
    union_path = os.path.join(data_dir, 'baltic_border_union.geojson')
    with open(union_path, 'r') as f:
        union_data = json.load(f)

    # Get largest component (main landmass)
    components = union_data['geometry']['coordinates']
    largest = max(components, key=lambda c: len(c[0]))
    main_polygon = largest[0]  # Outer ring

    print(f"\nInput polygon: {len(main_polygon)} vertices")

    # Extract Baltic Sea
    baltic_polygon = extract_baltic_sea(main_polygon)

    if baltic_polygon:
        # Save result
        baltic_geojson = {
            "type": "Feature",
            "properties": {
                "name": "Baltic Sea (Polygon Closing Method)",
                "method": "Closing between Skagen and Göteborg",
                "vertices": len(baltic_polygon)
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [baltic_polygon]
            }
        }

        output_path = os.path.join(test_data_dir, 'baltic_sea_extracted.geojson')
        with open(output_path, 'w') as f:
            json.dump(baltic_geojson, f, indent=2)

        print(f"\n{'=' * 60}")
        print(f"  Baltic Sea polygon saved to:")
        print(f"  {output_path}")
        print(f"\nResult:")
        print(f"  Vertices: {len(baltic_polygon)}")
        print(f"  Method: Polygon closing (superior to coastline extraction)")
        print(f"{'=' * 60}")
    else:
        print("\n  Failed to extract Baltic Sea polygon")
