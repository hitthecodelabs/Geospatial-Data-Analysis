def project_polygon(polygon, axis):
    """Projects a polygon onto an axis"""
    dots = [x * axis[0] + y * axis[1] for x, y in polygon]
    return min(dots), max(dots)

def polygons_intersect(poly1, poly2):
    """Uses the Separating Axis Theorem to check for polygon intersection"""
    edges = []
    
    # Get edges of both polygons
    for polygon in [poly1, poly2]:
        for i in range(len(polygon)):
            p1 = polygon[i]
            p2 = polygon[(i + 1) % len(polygon)]
            edge = (p2[0] - p1[0], p2[1] - p1[1])
            normal = (-edge[1], edge[0])  # Perpendicular vector
            edges.append(normal)

    # Check projections for overlap
    for axis in edges:
        min1, max1 = project_polygon(poly1, axis)
        min2, max2 = project_polygon(poly2, axis)
        if max1 < min2 or max2 < min1:  # No overlap on this axis means no intersection
            return False
    
    return True  # Overlapping on all axes means they intersect

# Example usage
polygon1 = [(0, 0), (2, 0), (2, 2), (0, 2)]
polygon2 = [(1, 1), (3, 1), (3, 3), (1, 3)]

if polygons_intersect(polygon1, polygon2):
    print("Polygons intersect.")
else:
    print("Polygons do not intersect.")
