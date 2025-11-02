#!/usr/bin/env python3
"""
Polygon triangulation using ear clipping algorithm.

Converts a simple polygon (no holes, no self-intersections) into triangles.
Note: quick and simple, not optimal!

OUTPUT: data/baltic_border_union.geojson, test-data/union_triangulated.geojson
"""
import json
import os
from .geometry import cross_product_2d, point_in_triangle, calculate_triangle_area, calculate_polygon_area


def is_ear(prev_idx, curr_idx, next_idx, polygon, remaining_indices):
    """
    Check if vertex at curr_idx forms an ear.

    An ear is a triangle formed by three consecutive vertices where:
    1. The triangle is counter-clockwise (convex)
    2. No other vertices of the polygon are inside the triangle

    Args:
        prev_idx, curr_idx, next_idx: Indices in remaining_indices list
        polygon: Original polygon coordinates
        remaining_indices: List of indices still in polygon

    Returns:
        True if curr forms an ear
    """
    # Get actual vertex indices
    i_prev = remaining_indices[prev_idx]
    i_curr = remaining_indices[curr_idx]
    i_next = remaining_indices[next_idx]

    # Get coordinates
    prev = polygon[i_prev]
    curr = polygon[i_curr]
    next_p = polygon[i_next]

    # Check if triangle is convex (counter-clockwise)
    cross = cross_product_2d(prev, curr, next_p)
    if cross <= 0:  # Clockwise or collinear - not an ear
        return False

    # Check if any other vertex is inside this triangle
    for idx in remaining_indices:
        # Skip the three vertices forming the triangle
        if idx == i_prev or idx == i_curr or idx == i_next:
            continue

        point = polygon[idx]
        if point_in_triangle(point, prev, curr, next_p):
            return False

    return True


def triangulate_polygon(polygon):
    """
    Triangulate a simple polygon using ear clipping algorithm.

    Args:
        polygon: List of [x, y] or [lon, lat] coordinates forming a simple polygon
                Must be counter-clockwise ordered

    Returns:
        List of triangles, where each triangle is [[x1,y1], [x2,y2], [x3,y3]]
    """
    # Make a copy and remove duplicate last point if present
    poly = [list(p) for p in polygon]
    if poly[0] == poly[-1]:
        poly = poly[:-1]

    n = len(poly)
    if n < 3:
        return []

    # If only 3 vertices, it's already a triangle
    if n == 3:
        return [poly]

    # Check if polygon is counter-clockwise, reverse if clockwise
    area = 0
    for i in range(n):
        j = (i + 1) % n
        area += poly[i][0] * poly[j][1]
        area -= poly[j][0] * poly[i][1]

    if area < 0:  # Clockwise, reverse it
        poly = poly[::-1]
        print("  Reversed polygon to counter-clockwise")

    triangles = []
    remaining_indices = list(range(n))

    # Ear clipping loop
    iterations = 0
    max_iterations = 2 * n  # Safety limit

    while len(remaining_indices) > 3 and iterations < max_iterations:
        iterations += 1

        # Try to find an ear
        ear_found = False
        for i in range(len(remaining_indices)):
            prev_idx = (i - 1) % len(remaining_indices)
            curr_idx = i
            next_idx = (i + 1) % len(remaining_indices)

            if is_ear(prev_idx, curr_idx, next_idx, poly, remaining_indices):
                # Found an ear! Cut it off
                i_prev = remaining_indices[prev_idx]
                i_curr = remaining_indices[curr_idx]
                i_next = remaining_indices[next_idx]

                triangle = [poly[i_prev], poly[i_curr], poly[i_next]]
                triangles.append(triangle)

                # Remove the ear vertex
                remaining_indices.pop(curr_idx)
                ear_found = True
                break

        if not ear_found:
            print(f"  Warning: No ear found after {iterations} iterations")
            print(f"  Remaining vertices: {len(remaining_indices)}")
            break

    # Add final triangle
    if len(remaining_indices) == 3:
        final_triangle = [poly[remaining_indices[0]],
                         poly[remaining_indices[1]],
                         poly[remaining_indices[2]]]
        triangles.append(final_triangle)

    return triangles


def test_triangulation():
    """Test triangulation on the union of Baltic-bordering countries."""

    # Get paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, '..', 'data')
    test_data_dir = os.path.join(data_dir, 'test-data')

    # Load Baltic border union polygon (from main data)
    union_path = os.path.join(data_dir, 'baltic_border_union.geojson')
    with open(union_path, 'r') as f:
        union_data = json.load(f)

    # Get all components
    components = union_data['geometry']['coordinates']

    # Find largest component (main landmass)
    largest = max(components, key=lambda c: len(c[0]))
    polygon = largest[0]  # Outer ring

    print(f"Baltic countries union (largest component): {len(polygon)} points")
    print(f"Triangulating...")

    triangles = triangulate_polygon(polygon)

    print(f"\n Triangulation complete!")
    print(f"  Input: {len(polygon)} vertices")
    print(f"  Output: {len(triangles)} triangles")
    print(f"  Expected: {len(polygon) - 2} triangles (Euler's formula)")

    if len(triangles) < len(polygon) - 2:
        print(f"    Missing {len(polygon) - 2 - len(triangles)} triangles")

    # Calculate area (sum of triangle areas)
    total_area = sum(calculate_triangle_area(t) for t in triangles)
    print(f"\nPolygon area: {total_area:.4f} square degrees")

    # Save triangulation result
    output_data = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"triangle_id": i},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [triangle + [triangle[0]]]  # Close the triangle
                }
            }
            for i, triangle in enumerate(triangles)
        ]
    }

    output_path = os.path.join(test_data_dir, 'union_triangulated.geojson')
    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"\nTriangulation saved to: {output_path}")
    print("You can visualize this in QGIS or geojson.io")

    return triangles


if __name__ == "__main__":
    test_triangulation()
