#!/usr/bin/env python3
"""
Polygon closing algorithm.

Given a polygon and two points on its boundary, creates a new polygon
by connecting the two points with an external edge and taking the shortest
path along the original polygon boundary.

OUTPUT: data/test-data/baltic_sea_closed.geojson
"""
import json
import os
from .geometry import (distance, find_closest_point_on_polygon,
                       segments_intersect, calculate_polygon_area)


def is_edge_external(polygon, idx1, idx2):
    """
    Check if edge between polygon[idx1] and polygon[idx2] is external
    (doesn't intersect the polygon interior).

    Args:
        polygon: List of polygon vertices
        idx1, idx2: Indices of points to connect

    Returns:
        True if edge is external (doesn't intersect any polygon edges
        except at the endpoints)
    """
    p1 = polygon[idx1]
    p2 = polygon[idx2]

    n = len(polygon)

    # Check against all polygon edges
    for i in range(n):
        j = (i + 1) % n

        # Skip edges that share an endpoint with our test edge
        if i == idx1 or i == idx2 or j == idx1 or j == idx2:
            continue

        # Check if test edge intersects this polygon edge
        if segments_intersect(p1, p2, polygon[i], polygon[j]):
            return False

    return True


def extract_path(polygon, start_idx, end_idx, direction='forward'):
    """
    Extract path along polygon from start_idx to end_idx.

    Args:
        polygon: List of polygon vertices
        start_idx: Starting index
        end_idx: Ending index
        direction: 'forward' or 'backward'

    Returns:
        List of vertices along the path (including start and end)
    """
    n = len(polygon)
    path = []

    if direction == 'forward':
        # Go forward from start to end
        if start_idx <= end_idx:
            path = polygon[start_idx:end_idx+1]
        else:
            # Wrap around
            path = polygon[start_idx:] + polygon[:end_idx+1]
    else:  # backward
        # Go backward from start to end
        if start_idx >= end_idx:
            path = polygon[start_idx:end_idx-1:-1] if end_idx > 0 else polygon[start_idx::-1]
            if end_idx == 0:
                path.append(polygon[0])
        else:
            # Wrap around backward
            path = polygon[start_idx::-1] + polygon[:end_idx-1:-1]
            if end_idx == 0:
                path.append(polygon[0])

    return path


def calculate_path_length(path):
    """Calculate total length of a path."""
    length = 0
    for i in range(len(path) - 1):
        length += distance(path[i], path[i+1])
    return length


def close_polygon(polygon, point1, point2):
    """
    Create a closed polygon by connecting two boundary points with an external edge.

    Args:
        polygon: List of [lon, lat] coordinates (should not have duplicate end point)
        point1: First point [lon, lat] (can be approximate, will find closest on polygon)
        point2: Second point [lon, lat] (can be approximate, will find closest on polygon)

    Returns:
        New polygon formed by external edge and shortest path between points,
        or None if edge is not external
    """
    # Make a copy and remove duplicate last point if present
    poly = [list(p) for p in polygon]
    if poly[0] == poly[-1]:
        poly = poly[:-1]

    # Find closest points on polygon boundary
    p1, idx1, dist1 = find_closest_point_on_polygon(poly, point1)
    p2, idx2, dist2 = find_closest_point_on_polygon(poly, point2)

    print(f"Found closest points:")
    print(f"  Point 1: {p1} at index {idx1} (distance: {dist1:.4f})")
    print(f"  Point 2: {p2} at index {idx2} (distance: {dist2:.4f})")

    # Check if connecting edge is external
    if not is_edge_external(poly, idx1, idx2):
        print("Warning: Edge is not external (intersects polygon)")
        return None

    print("  Edge is external")

    # Extract both possible paths
    path_forward = extract_path(poly, idx1, idx2, 'forward')
    path_backward = extract_path(poly, idx1, idx2, 'backward')

    # Calculate lengths
    len_forward = calculate_path_length(path_forward)
    len_backward = calculate_path_length(path_backward)

    print(f"\nPath analysis:")
    print(f"  Forward path: {len(path_forward)} vertices, length: {len_forward:.4f}")
    print(f"  Backward path: {len(path_backward)} vertices, length: {len_backward:.4f}")

    # Choose shorter path
    if len_forward <= len_backward:
        chosen_path = path_forward
        print(f"    Using forward path")
    else:
        chosen_path = path_backward
        print(f"    Using backward path")

    # Create new closed polygon: path + closing edge
    new_polygon = chosen_path + [chosen_path[0]]  # Close it

    return new_polygon


def test_closing():
    """Test polygon closing on Baltic states union."""

    # Get paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, '..', 'data')
    test_data_dir = os.path.join(data_dir, 'test-data')

    # Load Baltic border union polygon (from main data)
    union_path = os.path.join(data_dir, 'baltic_border_union.geojson')
    with open(union_path, 'r') as f:
        union_data = json.load(f)

    # Get largest component (main landmass)
    components = union_data['geometry']['coordinates']
    largest = max(components, key=lambda c: len(c[0]))
    polygon = largest[0]  # Outer ring

    print(f"Testing polygon closing on Baltic states union")
    print(f"Original polygon: {len(polygon)} vertices\n")

    # Reference points:
    # Skagen, Denmark: ~57.7°N, 10.6°E
    # Göteborg, Sweden: ~57.7°N, 11.9°E
    skagen = [10.6, 57.7]
    goteborg = [11.9, 57.7]

    print(f"Target points:")
    print(f"  Skagen, Denmark: {skagen}")
    print(f"  Göteborg, Sweden: {goteborg}\n")

    # Close polygon
    closed_polygon = close_polygon(polygon, skagen, goteborg)

    if closed_polygon is None:
        print("\n  Failed to close polygon (edge not external)")
        return

    print(f"\n  Polygon closing complete!")
    print(f"  New polygon: {len(closed_polygon)} vertices")

    # Calculate area
    area = calculate_polygon_area(closed_polygon)
    print(f"  Area: {area:.4f} square degrees")

    # Save result to test-data
    output_data = {
        "type": "Feature",
        "properties": {
            "name": "Baltic Sea (Extracted via closing)",
            "method": "Polygon closing between Skagen and Göteborg",
            "vertices": len(closed_polygon)
        },
        "geometry": {
            "type": "Polygon",
            "coordinates": [closed_polygon]
        }
    }

    output_path = os.path.join(test_data_dir, 'baltic_sea_closed.geojson')
    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"\n  Saved to: {output_path}")


if __name__ == "__main__":
    test_closing()
