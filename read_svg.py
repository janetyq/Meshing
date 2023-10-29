import xml.etree.ElementTree as ET
import svg.path
import matplotlib.pyplot as plt

# TODO:
# smartly specify cubic bezier curve resolution

def douglas_peucker(points, epsilon):
    '''
    Returns a simplified version of the given list of points using the Douglas-Peucker algorithm.
    '''
    if len(points) <= 2:
        return points
    dmax = 0
    pt_idx = None
    start, end = points[0], points[-1]
    vec = [end[0] - start[0], end[1] - start[1]]
    norm = (vec[0]**2 + vec[1]**2)**0.5
    for idx in range(1, len(points)-1):
        point = points[idx]
        cross = (point[0] - start[0]) * vec[1] - (point[1] - start[1]) * vec[0]
        d = abs(cross) / norm
        if d > dmax:
            dmax = d
            pt_idx = idx
    
    if dmax < epsilon:
        return [start, end]
    else:
        return douglas_peucker(points[:pt_idx+1], epsilon)[:-1] + douglas_peucker(points[pt_idx:], epsilon)

def remove_close_points(points, epsilon):
    '''
    Returns a list of points with points that are within epsilon of each other removed.
    '''
    new_points = []
    for i in range(len(points)):
        pt1 = points[i]
        pt2 = points[(i+1)%len(points)]
        distance = ((pt1[0] - pt2[0])**2 + (pt1[1] - pt2[1])**2)**0.5
        if distance > epsilon:
            new_points.append(points[i])
    return new_points

def calculate_polygon_area(points):
    '''
    Returns the area of a polygon defined by the given list of points.

    Uses the shoelace formula / Gauss's area formula.
    '''
    area = 0
    for i in range(len(points)):
        x1, y1 = points[i]
        x2, y2 = points[(i+1)%len(points)]

        area += 1/2 * (x1 - x2) * (y1 + y2)
    
    return abs(area)

def read_svg_to_list_of_path_coords(svg_file):
    # Read the SVG file and parse it
    tree = ET.parse(svg_file)
    root = tree.getroot()
    list_of_path_coords = []

    # Iterate over all path elements
    for path in root.findall(".//{http://www.w3.org/2000/svg}path"):
        d = path.get("d")
        svg_path = svg.path.parse_path(d)
        path_coords = []
        for segment in svg_path:
            start = [segment.start.real, segment.start.imag]
            end = [segment.end.real, segment.end.imag]
            if isinstance(segment, svg.path.path.Move):
                assert len(path_coords) == 0
                path_coords.append(start)
            elif isinstance(segment, svg.path.path.Line):
                path_coords.append(end)
            elif isinstance(segment, svg.path.path.Close):
                list_of_path_coords.append(path_coords)
                path_coords = []
            elif isinstance(segment, svg.path.path.CubicBezier):
                # Approximate the cubic Bezier curve with line segments
                control1 = (segment.control1.real, segment.control1.imag)
                control2 = (segment.control2.real, segment.control2.imag)
                num_segments = 5
                for t in range(1, num_segments):
                    t_normalized = t / num_segments
                    x = (1 - t_normalized)**3 * start[0] + 3 * (1 - t_normalized)**2 * t_normalized * control1[0] + 3 * (1 - t_normalized) * t_normalized**2 * control2[0] + t_normalized**3 * end[0]
                    y = (1 - t_normalized)**3 * start[1] + 3 * (1 - t_normalized)**2 * t_normalized * control1[1] + 3 * (1 - t_normalized) * t_normalized**2 * control2[1] + t_normalized**3 * end[1]
                    path_coords.append([x, y])
            
    return list_of_path_coords

def process_list_of_path_coords(list_of_path_coords, epsilon=0, min_area=0):
    path_segments = []
    for path_coords in list_of_path_coords:
        area = calculate_polygon_area(path_coords)
        if area > min_area:
            if epsilon > 0:
                path_coords = douglas_peucker(path_coords, epsilon)
                path_coords = remove_close_points(path_coords, 10)
            path_len = len(path_coords)
            path_segments.extend([[path_coords[i], path_coords[(i+1)%path_len]] for i in range(path_len)])
    
    return path_segments


def read_and_process_svg(svg_file, epsilon=0, min_area=0):
    '''
    Returns a list of line segments from the given SVG file.

    Line segments are simplified with the Douglas-Peucker algorithm with the given epsilon.
    Closed paths with an area less than min_area are ignored.
    '''
    list_of_path_coords = read_svg_to_list_of_path_coords(svg_file)
    path_segments = process_list_of_path_coords(list_of_path_coords, epsilon, min_area)
    
    vertices = set([tuple(vertex) for path_seg in path_segments for vertex in path_seg])
    vertices = [list(vertex) for vertex in vertices]
    segments = []

    for path_seg in path_segments:
        segment = [vertices.index(path_seg[0]), vertices.index(path_seg[1])]
        segments.append(segment)

    return vertices, segments

if __name__ == '__main__':
    V, S = read_and_process_svg('outline-ca.svg', epsilon=0, min_area=0)

    # Display the svg image
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    ax.set_aspect('equal')
    for seg in S:
        start = V[seg[0]]
        end = V[seg[1]]
        ax.plot([start[0], end[0]], [start[1], end[1]], color='black')
    plt.show()
