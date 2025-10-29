#!/usr/bin/env python3
"""
Common geometric operations for 2D points, lines, and polygons.

Coordinates are represented as [x, y] or [lon, lat] lists.
"""
import math


# ============================================================================
# Basic 2D Operations
# ============================================================================

def distance(p1, p2):
    """
    Calculate Euclidean distance between two points.

    Args:
        p1, p2: Points as [x, y] or [lon, lat]

    Returns:
        Distance between points
    """
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)


def cross_product_2d(o, a, b):
    """
    Calculate 2D cross product of vectors OA and OB.

    Returns the z-component of the 3D cross product:
    |OA0 OA1 0|
    |OB0 OB1 0|
    | x   y  z|

    Args:
        o: Origin point [x, y]
        a: First point [x, y]
        b: Second point [x, y]

    Returns:
        Positive if counter-clockwise, negative if clockwise, 0 if collinear
    """
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


# ============================================================================
# Line and Segment Operations
# ============================================================================

def on_segment(p, q, r):
    """
    Check if point q lies on line segment pr (assuming p, q, r are collinear).

    Args:
        p, q, r: Points as [x, y]

    Returns:
        True if q is on segment pr
    """
    return (min(p[0], r[0]) <= q[0] <= max(p[0], r[0]) and
            min(p[1], r[1]) <= q[1] <= max(p[1], r[1]))


def segments_intersect(p1, p2, p3, p4):
    """
    Check if line segment p1-p2 intersects with segment p3-p4.

    Uses orientation test (cross product) to check if segments straddle
    each other.

    Args:
        p1, p2: First segment endpoints [x, y]
        p3, p4: Second segment endpoints [x, y]

    Returns:
        True if segments intersect (including touching at endpoints)
    """
    d1 = cross_product_2d(p3, p4, p1)
    d2 = cross_product_2d(p3, p4, p2)
    d3 = cross_product_2d(p1, p2, p3)
    d4 = cross_product_2d(p1, p2, p4)

    # Proper intersection (segments cross each other)
    if ((d1 > 0 and d2 < 0) or (d1 < 0 and d2 > 0)) and \
       ((d3 > 0 and d4 < 0) or (d3 < 0 and d4 > 0)):
        return True

    # Check if points are collinear and overlapping
    if d1 == 0 and on_segment(p3, p1, p4):
        return True
    if d2 == 0 and on_segment(p3, p2, p4):
        return True
    if d3 == 0 and on_segment(p1, p3, p2):
        return True
    if d4 == 0 and on_segment(p1, p4, p2):
        return True

    return False


# ============================================================================
# Triangle Operations
# ============================================================================

def point_in_triangle(p, a, b, c):
    """
    Test if point p is inside triangle ABC using barycentric coordinates.

    Uses cross products to check if point is on the same side of all edges.

    Args:
        p: Point to test [x, y]
        a, b, c: Triangle vertices [x, y]

    Returns:
        True if p is inside triangle ABC (including on edges)
    """
    # Use cross products to check if point is on same side of all edges
    d1 = cross_product_2d(a, b, p)
    d2 = cross_product_2d(b, c, p)
    d3 = cross_product_2d(c, a, p)

    # Point is inside if all cross products have same sign
    has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
    has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)

    return not (has_neg and has_pos)


def calculate_triangle_area(triangle):
    """
    Calculate area of a triangle using cross product (shoelace formula).

    Args:
        triangle: [[x1,y1], [x2,y2], [x3,y3]]

    Returns:
        Area of triangle (always positive)
    """
    a, b, c = triangle
    area = 0.5 * abs(cross_product_2d(a, b, c))
    return area


# ============================================================================
# Polygon Operations
# ============================================================================

def normalize_edge(p1, p2):
    """
    Normalize edge to have consistent direction for comparison.

    Returns edge in canonical form (lexicographically smaller point first).
    Useful for detecting duplicate edges in opposite directions.

    Args:
        p1, p2: Edge endpoints (lists or tuples)

    Returns:
        Tuple of (point1, point2) with point1 <= point2
    """
    tp1 = tuple(p1) if not isinstance(p1, tuple) else p1
    tp2 = tuple(p2) if not isinstance(p2, tuple) else p2

    if tp1 < tp2:
        return (tp1, tp2)
    else:
        return (tp2, tp1)


def extract_edges(polygon_coords):
    """
    Extract all edges from a polygon as pairs of consecutive points.

    Args:
        polygon_coords: List of [x, y] coordinates

    Returns:
        List of edges as tuples ((x1, y1), (x2, y2))
    """
    edges = []
    n = len(polygon_coords)
    for i in range(n):
        p1 = polygon_coords[i]
        p2 = polygon_coords[(i + 1) % n]
        edges.append((tuple(p1), tuple(p2)))
    return edges


def calculate_polygon_area(polygon):
    """
    Calculate area of a polygon using the shoelace formula.

    Args:
        polygon: List of [x, y] coordinates (closed or open)

    Returns:
        Area of polygon (always positive)
    """
    # Handle closed polygons (last point = first point)
    coords = polygon[:-1] if polygon[0] == polygon[-1] else polygon

    area = 0
    n = len(coords)
    for i in range(n):
        j = (i + 1) % n
        area += coords[i][0] * coords[j][1]
        area -= coords[j][0] * coords[i][1]

    return abs(area) / 2.0


def find_closest_point_on_polygon(polygon, target):
    """
    Find the closest point on polygon boundary to a target point.

    Args:
        polygon: List of [x, y] coordinates
        target: Target point [x, y]

    Returns:
        Tuple of (closest_point, index_in_polygon, distance)
    """
    min_dist = float('inf')
    closest_point = None
    closest_idx = -1

    for i, point in enumerate(polygon):
        dist = distance(point, target)
        if dist < min_dist:
            min_dist = dist
            closest_point = point
            closest_idx = i

    return closest_point, closest_idx, min_dist


def get_polygon_from_geojson(geometry):
    """
    Extract polygon coordinates from GeoJSON geometry.

    Handles both Polygon and MultiPolygon types.

    Args:
        geometry: GeoJSON geometry dict with 'type' and 'coordinates'

    Returns:
        List of polygon rings (each ring is a list of [lon, lat])
    """
    polygons = []

    if geometry['type'] == 'Polygon':
        # Polygon has one outer ring (and optional holes)
        polygons.append(geometry['coordinates'][0])
    elif geometry['type'] == 'MultiPolygon':
        # MultiPolygon has multiple polygons
        for poly in geometry['coordinates']:
            polygons.append(poly[0])  # Outer ring of each polygon

    return polygons
