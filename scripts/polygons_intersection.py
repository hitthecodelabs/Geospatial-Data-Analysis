import json
from glob import glob

# Function to create a list of tuples representing a polygon from cartas data
def create_polygon_from_bounds(data):
    """
    Creates a rectangular polygon represented as a list of (x, y) tuples
    based on the minimum and maximum UTM coordinates found in the input data dictionary.

    Args:
        data (dict): A dictionary containing keys like 'XMin_utm', 'YMin_utm',
                     'XMax_utm', 'YMax_utm', and optionally 'name'.

    Returns:
        list: A list of (x, y) tuples representing the vertices of the rectangle
              in counter-clockwise order, starting from the bottom-left corner.
              The polygon is explicitly closed (first and last points are the same).
        None: If any of the required keys ('XMin_utm', 'YMin_utm', 'XMax_utm',
              'YMax_utm') are missing in the input data. An error message
              is printed in this case.
    """
    try:
        # Define the four corners of the rectangle using min/max coordinates
        points = [
            (data["XMin_utm"], data["YMin_utm"]), # Bottom-left
            (data["XMin_utm"], data["YMax_utm"]), # Top-left
            (data["XMax_utm"], data["YMax_utm"]), # Top-right
            (data["XMax_utm"], data["YMin_utm"]), # Bottom-right
            (data["XMin_utm"], data["YMin_utm"])  # Closing the polygon explicitly by repeating the start point
        ]
        return points
    except KeyError as e:
        # Handle cases where the input dictionary is missing required coordinate keys
        print(f"Error: Missing key {e} in data item: {data.get('name', 'N/A')}")
        return None # Indicate failure to create the polygon


def point_in_polygon(x, y, polygon):
    """
    Check if a point (x, y) is strictly inside a given polygon using the Ray Casting algorithm.

    The algorithm works by drawing a horizontal ray from the point to the right (positive x direction)
    and counting how many times it intersects with the edges of the polygon. If the number of
    intersections is odd, the point is inside; if even, it's outside.

    Args:
        x (float): The x-coordinate of the point to check.
        y (float): The y-coordinate of the point to check.
        polygon (list): A list of (x, y) tuples representing the vertices of the polygon
                        in order (clockwise or counter-clockwise). The polygon should be closed
                        (or the algorithm handles the wrap-around).

    Returns:
        bool: True if the point (x, y) is inside the polygon, False otherwise.

    Note:
        This implementation might have issues with points lying exactly on horizontal edges
        or vertices. It generally works well for strictly inside/outside checks.
    """
    n = len(polygon)
    inside = False  # Initialize result: assume point is outside

    # Get the first vertex of the polygon
    p1x, p1y = polygon[0]

    # Loop through each edge of the polygon (from vertex i to vertex i+1)
    for i in range(n + 1):
        # Get the second vertex of the current edge.
        # Use modulo n to wrap around to the first vertex for the last edge.
        p2x, p2y = polygon[i % n]

        # Check if the horizontal ray passes between the y-coordinates of the edge's endpoints
        if y > min(p1y, p2y):  # Point's y is above the lower endpoint of the edge
            if y <= max(p1y, p2y): # Point's y is not above the upper endpoint of the edge
                # Check if the point is to the left of the rightmost endpoint of the edge
                if x <= max(p1x, p2x):
                    # If the edge is not horizontal
                    if p1y != p2y:
                        # Calculate the x-coordinate where the horizontal ray intersects the edge
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    # If the edge is vertical (p1x == p2x) or the point's x is to the left of the intersection
                    if p1x == p2x or x <= xinters:
                        # Found an intersection, flip the 'inside' status
                        inside = not inside

        # Move to the next edge: the second point of the current edge becomes the first point of the next
        p1x, p1y = p2x, p2y

    return inside

def is_point_on_segment(p1, p2, q):
    """
    Check if point q lies on the line segment defined by endpoints p1 and p2.

    This checks for collinearity and also ensures that q is between p1 and p2 (inclusive).

    Args:
        p1 (tuple): Coordinates (x, y) of the first endpoint of the segment.
        p2 (tuple): Coordinates (x, y) of the second endpoint of the segment.
        q (tuple): Coordinates (x, y) of the point to check.

    Returns:
        bool: True if point q is on the line segment p1p2, False otherwise.
    """
    # Check if q's x-coordinate is within the range of p1's and p2's x-coordinates
    x_in_range = min(p1[0], p2[0]) <= q[0] <= max(p1[0], p2[0])
    # Check if q's y-coordinate is within the range of p1's and p2's y-coordinates
    y_in_range = min(p1[1], p2[1]) <= q[1] <= max(p1[1], p2[1])

    # Check if the points are collinear using the cross product (should be zero for collinear)
    # This is implicitly handled by do_segments_intersect, but explicitly stated here:
    # A more robust check would explicitly calculate the cross product:
    # colinear = (p2[1] - p1[1]) * (q[0] - p2[0]) == (q[1] - p2[1]) * (p2[0] - p1[0])
    # However, for the use within do_segments_intersect, checking the bounding box
    # after confirming a cross_product of 0 is sufficient.

    # The point q is on the segment if it's within the bounding box of the segment
    # AND the points are collinear (which is checked by cross_product being 0 in the calling function).
    return x_in_range and y_in_range


def cross_product(p1, p2, p3):
    """
    Compute the 2D cross product of vectors p1p2 and p1p3.

    The sign of the cross product indicates the orientation of p3 relative to the
    directed line segment p1p2:
        > 0: p3 is to the 'left' (counter-clockwise turn from p1p2 to p1p3)
        < 0: p3 is to the 'right' (clockwise turn)
        = 0: p1, p2, p3 are collinear

    Args:
        p1 (tuple): Coordinates (x, y) of the origin point.
        p2 (tuple): Coordinates (x, y) defining the end of the first vector (p1p2).
        p3 (tuple): Coordinates (x, y) defining the end of the second vector (p1p3).

    Returns:
        float: The magnitude of the 2D cross product.
    """
    # Vector p1p2 = (p2[0] - p1[0], p2[1] - p1[1])
    # Vector p1p3 = (p3[0] - p1[0], p3[1] - p1[1])
    # Cross product (p1p2) x (p1p3) = (p2[0] - p1[0]) * (p3[1] - p1[1]) - (p2[1] - p1[1]) * (p3[0] - p1[0])
    return (p2[0] - p1[0]) * (p3[1] - p1[1]) - (p2[1] - p1[1]) * (p3[0] - p1[0])

def do_segments_intersect(p1, q1, p2, q2):
    """
    Check if the line segment p1q1 intersects with the line segment p2q2.

    Uses the cross-product method to determine if the segments intersect. It handles
    general cases and collinear cases where segments overlap or touch at an endpoint.

    Args:
        p1 (tuple): Coordinates (x, y) of the first endpoint of the first segment.
        q1 (tuple): Coordinates (x, y) of the second endpoint of the first segment.
        p2 (tuple): Coordinates (x, y) of the first endpoint of the second segment.
        q2 (tuple): Coordinates (x, y) of the second endpoint of the second segment.

    Returns:
        bool: True if the segments intersect, False otherwise.
    """
    # Calculate the orientation of p1 and q1 relative to the segment p2q2.
    # d1 = cross_product(p2, q2, p1) indicates orientation of p1 w.r.t. p2q2
    d1 = cross_product(p2, q2, p1)
    # d2 = cross_product(p2, q2, q1) indicates orientation of q1 w.r.t. p2q2
    d2 = cross_product(p2, q2, q1)

    # Calculate the orientation of p2 and q2 relative to the segment p1q1.
    # d3 = cross_product(p1, q1, p2) indicates orientation of p2 w.r.t. p1q1
    d3 = cross_product(p1, q1, p2)
    # d4 = cross_product(p1, q1, q2) indicates orientation of q2 w.r.t. p1q1
    d4 = cross_product(p1, q1, q2)

    # General case: Segments intersect if the endpoints of each segment lie on opposite sides
    # of the line defined by the other segment. This happens when the cross products have
    # different signs.
    if d1 * d2 < 0 and d3 * d4 < 0:
        return True  # Segments properly intersect (cross each other)

    # Collinear cases:
    # If d1 is 0, p1 is collinear with p2q2. Check if p1 lies *on* the segment p2q2.
    if d1 == 0 and is_point_on_segment(p2, q2, p1):
        return True
    # If d2 is 0, q1 is collinear with p2q2. Check if q1 lies *on* the segment p2q2.
    if d2 == 0 and is_point_on_segment(p2, q2, q1):
        return True
    # If d3 is 0, p2 is collinear with p1q1. Check if p2 lies *on* the segment p1q1.
    if d3 == 0 and is_point_on_segment(p1, q1, p2):
        return True
    # If d4 is 0, q2 is collinear with p1q1. Check if q2 lies *on* the segment p1q1.
    if d4 == 0 and is_point_on_segment(p1, q1, q2):
        return True

    # If none of the above conditions are met, the segments do not intersect.
    return False


def do_polygons_intersect(poly1, poly2):
    """
    Check if two convex or non-convex polygons intersect or overlap.

    This function checks for intersection using three conditions:
    1. Any vertex of poly1 is inside poly2.
    2. Any vertex of poly2 is inside poly1.
    3. Any edge of poly1 intersects with any edge of poly2.

    If any of these conditions are true, the polygons are considered intersecting.

    Args:
        poly1 (list): A list of (x, y) tuples representing the vertices of the first polygon.
                      Vertices should be ordered (e.g., clockwise or counter-clockwise).
                      The polygon is assumed closed (last vertex connects to the first).
        poly2 (list): A list of (x, y) tuples representing the vertices of the second polygon.
                      Vertices should be ordered. Assumed closed.

    Returns:
        bool: True if the polygons intersect or overlap, False otherwise.

    Dependencies:
        - point_in_polygon(x, y, polygon)
        - do_segments_intersect(p1, q1, p2, q2)
    """
    # Get the number of vertices for each polygon
    n1, n2 = len(poly1), len(poly2)

    # --- Check 1: Test if any vertex of the first polygon lies inside the second polygon. ---
    # This covers cases where poly1 is fully contained within poly2, or they partially
    # overlap such that a vertex of poly1 penetrates poly2's area.
    for v in poly1:
        # Use the point_in_polygon function to check if the vertex 'v' is inside poly2
        if point_in_polygon(v[0], v[1], poly2):
            # If any vertex of poly1 is inside poly2, the polygons intersect.
            # print(f"Intersection found: Vertex {v} of poly1 is inside poly2.") # Optional debug print
            return True

    # --- Check 2: Test if any vertex of the second polygon lies inside the first polygon. ---
    # This is necessary because Check 1 is not symmetric (poly1 inside poly2 doesn't mean
    # poly2 is inside poly1 unless they are identical). This covers cases where poly2
    # is fully contained within poly1 or they overlap such that a vertex of poly2 penetrates poly1.
    for v in poly2:
        # Use the point_in_polygon function to check if the vertex 'v' is inside poly1
        if point_in_polygon(v[0], v[1], poly1):
            # If any vertex of poly2 is inside poly1, the polygons intersect.
            # print(f"Intersection found: Vertex {v} of poly2 is inside poly1.") # Optional debug print
            return True

    # --- Check 3: Test if any edge of the first polygon intersects with any edge of the second polygon. ---
    # This covers cases where the polygons cross each other without any vertex necessarily
    # being inside the other polygon (e.g., two overlapping squares forming a plus shape,
    # or polygons just touching at edges).
    for i in range(n1): # Iterate through each edge of poly1
        # Define the first edge (p1, q1) from poly1.
        # The edge connects vertex i to vertex (i+1).
        # Use modulo n1 to handle the wrap-around from the last vertex back to the first.
        p1 = poly1[i]                 # Start point of edge i in poly1
        q1 = poly1[(i + 1) % n1]      # End point of edge i in poly1

        for j in range(n2): # Iterate through each edge of poly2
            # Define the second edge (p2, q2) from poly2.
            # The edge connects vertex j to vertex (j+1).
            # Use modulo n2 to handle the wrap-around.
            p2 = poly2[j]             # Start point of edge j in poly2
            q2 = poly2[(j + 1) % n2]  # End point of edge j in poly2

            # Use the segment intersection helper function to check if edge (p1, q1)
            # intersects with edge (p2, q2).
            if do_segments_intersect(p1, q1, p2, q2):
                # If any pair of edges intersects, the polygons intersect.
                # print(f"Intersection found: Edge {p1}-{q1} of poly1 intersects Edge {p2}-{q2} of poly2.") # Optional debug print
                return True

    # --- No Intersection Found ---
    # If none of the above checks (vertex inside, edge intersection) returned True,
    # then the polygons do not intersect according to these tests.
    return False

utm_coords = []

cartas = json.load(open("datass.json", "r", encoding="utf-8"))

# Create polygon representations (list of tuples) from the loaded data
# Store as (index, polygon_vertices, name)
cartas_polygons = []
for i, item in enumerate(cartas):
    if isinstance(item, dict): # Basic check if item is a dictionary
        polygon_vertices = create_polygon_from_bounds(item)
        if polygon_vertices: # Only add if polygon creation was successful
           cartas_polygons.append((i, polygon_vertices, item.get("name", f"Unnamed Carta {i}")))
        else:print(f"Skipping item {i} due to missing coordinate keys.")
    else:print(f"Warning: Skipping item {i} as it is not a dictionary: {item}")

for k in cartas_polygons:
    # print(i)
    carta_box = []
    for i in k[1]:carta_box.append([i[0], i[1]])
    
    status = do_polygons_intersect(utm_coords, carta_box) ### this one
    if status:
        print(f"✅ Polygons intersect: {k[2]}")
        print("-------------------------------------------------------")
    else:pass
    # print("❌ Polygons do not intersect.")
