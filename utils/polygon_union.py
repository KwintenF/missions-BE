#!/usr/bin/env python3
"""
Simple polygon union algorithm without external geometry libraries.

OUTPUT: data/baltic_border_union.geojson
"""
import json
from .geometry import normalize_edge, extract_edges, get_polygon_from_geojson


def union_polygons(geojson_features):
    """
    Union multiple GeoJSON polygon features into one.

    Algorithm:
    1. Extract all edges from all polygons
    2. Count edge occurrences (treating reversed edges as same)
    3. Keep edges that appear exactly once (outer boundary)
    4. Chain edges together to form union polygon

    Args:
        geojson_features: List of GeoJSON feature dicts with Polygon/MultiPolygon geometry

    Returns:
        List of [lon, lat] coordinates forming the union polygon
    """
    # Step 1: Extract all edges from all input polygons
    all_edges = []
    edge_count = {}
    directed_edges = {}  # Maps normalized edge to actual directed edges

    for feature in geojson_features:
        polygons = get_polygon_from_geojson(feature['geometry'])

        for polygon in polygons:
            edges = extract_edges(polygon)
            all_edges.extend(edges)

            for edge in edges:
                # Normalize edge for counting
                norm_edge = normalize_edge(edge[0], edge[1])
                edge_count[norm_edge] = edge_count.get(norm_edge, 0) + 1

                # Keep track of directed edges
                if norm_edge not in directed_edges:
                    directed_edges[norm_edge] = []
                directed_edges[norm_edge].append(edge)

    # Step 2: Find boundary edges (appear exactly once)
    boundary_edges = []
    for edge in all_edges:
        norm_edge = normalize_edge(edge[0], edge[1])
        if edge_count[norm_edge] == 1:
            boundary_edges.append(edge)

    if not boundary_edges:
        print("No boundary edges found!")
        return []

    print(f"Total edges: {len(all_edges)}")
    print(f"Boundary edges: {len(boundary_edges)}")
    print(f"Internal edges: {len(all_edges) - len(boundary_edges)}")

    # Step 3: Build adjacency for chaining edges (bidirectional)
    adjacency = {}  # point -> list of (next_point, edge_object) tuples
    edge_objects = set(boundary_edges)  # Track which edges exist

    for edge in boundary_edges:
        p1, p2 = edge
        # Add both directions
        if p1 not in adjacency:
            adjacency[p1] = []
        if p2 not in adjacency:
            adjacency[p2] = []
        adjacency[p1].append(p2)
        adjacency[p2].append(p1)

    # Step 4: Chain edges together to form polygon(s)
    if not adjacency:
        print("No adjacency built!")
        return []

    visited = set()
    polygons = []

    # May need to build multiple polygons (disconnected components)
    while len(visited) < len(boundary_edges):
        # Find unvisited edge
        start_point = None
        for edge in boundary_edges:
            if edge not in visited:
                start_point = edge[0]
                break

        if start_point is None:
            break

        # Trace polygon from start_point
        current_point = start_point
        polygon = [list(current_point)]
        path_edges = []

        for _ in range(len(boundary_edges) + 1):  # Safety limit
            if current_point not in adjacency:
                break

            # Find next unvisited edge
            next_point = None
            for candidate in adjacency[current_point]:
                edge_fwd = (current_point, candidate)
                edge_rev = (candidate, current_point)

                # Check if this edge hasn't been used
                if edge_fwd not in visited and edge_rev not in visited:
                    # Check if edge exists in original boundary
                    if edge_fwd in edge_objects or edge_rev in edge_objects:
                        next_point = candidate
                        # Mark edge as visited
                        if edge_fwd in edge_objects:
                            visited.add(edge_fwd)
                            path_edges.append(edge_fwd)
                        else:
                            visited.add(edge_rev)
                            path_edges.append(edge_rev)
                        break

            if next_point is None:
                # Dead end - try to close loop
                break

            # Check if we completed the loop
            if next_point == start_point:
                break

            polygon.append(list(next_point))
            current_point = next_point

        print(f"  Found polygon component with {len(polygon)} points")
        polygons.append(polygon)

    print(f"Union created {len(polygons)} polygon component(s)")
    print(f"Total points: {sum(len(p) for p in polygons)}")

    # Show component sizes
    sorted_polygons = sorted(polygons, key=len, reverse=True)
    print(f"Top 5 components by size: {[len(p) for p in sorted_polygons[:5]]}")

    # Return all components as MultiPolygon coordinates, filter out single-point artifacts
    valid_polygons = [p for p in polygons if len(p) >= 3]
    print(f"Returning {len(valid_polygons)} valid components (filtered out {len(polygons) - len(valid_polygons)} artifacts)")

    return valid_polygons


def test_baltic_union():
    """Test by unioning all Baltic Sea bordering countries (including mission countries)."""
    import os

    # Get path relative to utils/ directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, '..', 'data')

    # Load Natural Earth data
    ne_path = os.path.join(data_dir, 'ne_110m_admin_0_countries.geojson')
    with open(ne_path, 'r') as f:
        data = json.load(f)

    # All countries bordering the Baltic Sea (including Eastern Flank mission countries)
    baltic_neighbors = ['Sweden', 'Finland', 'Russia', 'Poland', 'Germany', 'Denmark',
                        'Estonia', 'Latvia', 'Lithuania']

    # Extract features for Baltic neighbors
    features = []
    for feature in data['features']:
        country_name = feature['properties'].get('NAME')
        if country_name in baltic_neighbors:
            features.append(feature)
            print(f"Found: {country_name}")

    print(f"\nUnioning {len(features)} countries...")
    union_polygon = union_polygons(features)

    if union_polygon:
        print(f"\nUnion successful!")

        # Save result as MultiPolygon
        result = {
            "type": "Feature",
            "properties": {"name": "Baltic Bordering Countries Union"},
            "geometry": {
                "type": "MultiPolygon",
                "coordinates": [[p] for p in union_polygon]  # Each polygon wrapped
            }
        }

        output_path = os.path.join(data_dir, 'baltic_border_union.geojson')
        with open(output_path, 'w') as f:
            json.dump(result, f, indent=2)

        print(f"\nSaved to: {output_path}")
        print(f"Components: {len(union_polygon)}")
        print(f"Largest component: {len(max(union_polygon, key=len))} points")
        return union_polygon
    else:
        print("Union failed!")
        return None


if __name__ == "__main__":
    test_baltic_union()
