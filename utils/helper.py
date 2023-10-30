from math import sqrt, pi, cos, acos

# useful functions used across all files

def calc_circumcircle(triangle_points):
    '''
    triangle_points: list of 3 points in the form [x, y]

    Returns the center and radius of the circumcircle of the triangle
    '''
    vecs = [triangle_points[i] - triangle_points[(i+1)%3] for i in range(3)]
    mids = [0.5 * (triangle_points[i] + triangle_points[(i+1)%3]) for i in range(3)]
    perps = [[vec[1], -vec[0]] for vec in vecs]

    # remove bisectors with 0 slope
    for i in range(3):
        if perps[i][0] == 0:
            perps.pop(i)
            mids.pop(i)
            break

    # calculate center using intersection of bisectors
    s1, s2 = [perp[1] / perp[0] for perp in perps[:2]]
    m1, m2 = mids[:2]
    x = (m2[1] - m1[1] + m1[0]*s1 - m2[0]*s2) / (s1 - s2)
    y = m1[1] + s1*(x - m1[0])
    center = [x, y]

    a, b, c = [calc_len(vec) for vec in vecs]
    radius = a*b*c / sqrt((a+b+c)*(b+c-a)*(c+a-b)*(a+b-c))
    
    return center, radius

def calc_len(vec):
    return (vec[0]**2 + vec[1]**2)**0.5

def calc_dot(vec1, vec2):
    return vec1[0]*vec2[0] + vec1[1]*vec2[1]

def calc_area(triangle_points):
    vec1 = triangle_points[1] - triangle_points[0]
    vec2 = triangle_points[2] - triangle_points[0]
    return abs(vec1[0]*vec2[1] - vec1[1]*vec2[0]) / 2

def get_min_angle(triangle):
    sides = [triangle[i] - triangle[(i+1)%3] for i in range(3)]
    lengths = [calc_len(side) for side in sides]
    i = lengths.index(min(lengths))
    if i == 0:
        angle = acos(abs(calc_dot(sides[1], sides[2]) / (lengths[1] * lengths[2])))
    elif i == 1:
        angle = acos(abs(calc_dot(sides[0], sides[2]) / (lengths[0] * lengths[2])))
    elif i == 2:
        angle = acos(abs(calc_dot(sides[0], sides[1]) / (lengths[0] * lengths[1])))
    return angle * 180 / pi

def intersect(pt1, pt2, pt3, pt4):
    x1, y1 = pt1
    x2, y2 = pt2
    x3, y3 = pt3
    x4, y4 = pt4

    denom = (x1-x2)*(y3-y4) - (y1-y2)*(x3-x4)
    if denom == 0:
        return False
    t = ((x1-x3)*(y3-y4) - (y1-y3)*(x3-x4)) / denom
    u = -((x1-x2)*(y1-y3) - (y1-y2)*(x1-x3)) / denom
    return 0 <= t <= 1 and 0 <= u <= 1

def point_in_polygon_points(point, polygon_points):
    count = 0
    polygon_edges = [(polygon_points[i], polygon_points[(i+1)%len(polygon_points)]) for i in range(len(polygon_points))]
    max_x = max([abs(edge[0][0]) for edge in polygon_edges])
    max_y = max([abs(edge[0][1]) for edge in polygon_edges])
    far_point = (2*max_x, 2*max_y)
    for edge in polygon_edges:
        point = (point[0], point[1])
        edge1_pt = (edge[0][0], edge[0][1])
        edge2_pt = (edge[1][0], edge[1][1])
        if intersect(point, far_point, edge1_pt, edge2_pt):
            count += 1
    return count % 2 == 1

def point_in_polygon_edges(point, polygon_edges):
    count = 0
    max_x = max([abs(edge[0][0]) for edge in polygon_edges])
    max_y = max([abs(edge[0][1]) for edge in polygon_edges])
    far_point = (2*max_x, 2*max_y)
    for edge in polygon_edges:
        point = (point[0], point[1])
        edge1_pt = (edge[0][0], edge[0][1])
        edge2_pt = (edge[1][0], edge[1][1])
        if intersect(point, far_point, edge1_pt, edge2_pt):
            count += 1
    return count % 2 == 1