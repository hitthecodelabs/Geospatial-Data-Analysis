def get_bounding_box(polygon):
    """Returns the bounding box (min_x, min_y, max_x, max_y) of a polygon"""
    xs, ys = zip(*polygon)
    return min(xs), min(ys), max(xs), max(ys)

def bounding_boxes_intersect(poly1, poly2):
    """Checks if bounding boxes of two polygons intersect"""
    min_x1, min_y1, max_x1, max_y1 = get_bounding_box(poly1)
    min_x2, min_y2, max_x2, max_y2 = get_bounding_box(poly2)

    return not (max_x1 < min_x2 or max_x2 < min_x1 or max_y1 < min_y2 or max_y2 < min_y1)

# Example usage:
polygon1 = [(0, 0), (2, 0), (2, 2), (0, 2)]  # Square from (0,0) to (2,2)
polygon2 = [(1, 1), (3, 1), (3, 3), (1, 3)]  # Square from (1,1) to (3,3)

if bounding_boxes_intersect(polygon1, polygon2):
    print("Bounding boxes intersect.")
else:
    print("No intersection.")
