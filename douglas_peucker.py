def douglas_peucker(points, epsilon):
    '''
    Returns a simplified version of the given list of points using the Douglas-Peucker algorithm.

    The algorithm works by removing points that are too close to a line segment between pairs of points on the path.
    This way it reduces the number of points while preserving the overall shape of the path.
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