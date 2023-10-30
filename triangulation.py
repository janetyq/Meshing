import numpy as np
import matplotlib.pyplot as plt
from helper import *

# TODO: refactor

class Triangulation:
    def __init__(self):
        self.points = np.empty((0, 2), dtype=float)
        self.triangles = set()

    def add_point(self, point):
        self.points = np.append(self.points, point[np.newaxis, :], axis=0)
        point_idx = len(self.points) - 1
        return point_idx

    def add_triangle(self, triangle):
        self.triangles.add(triangle)
        
    def remove_triangle(self, triangle):
        self.triangles.remove(triangle)
    
    def display(self, show=True):
        plt.title('Bowyer-Watson Method for Delaunay Triangulation')
        for point in self.points:
            plt.plot(point[0], point[1], 'o')
        plt.triplot(self.points[:,0], self.points[:,1], [list(triangle) for triangle in self.triangles])
        if show:
            plt.show()

    def __repr__(self):
        return f'Triangulation(\npoints={self.points}, \ntriangles={self.triangles})'
            

def get_triangle_edges(triangle):
    triangle_edges = [
        sorted([triangle[0], triangle[1]]),
        sorted([triangle[1], triangle[2]]),
        sorted([triangle[2], triangle[0]])
    ]
    return triangle_edges

def get_super_triangle(points):
    N = len(points)
    min_x, max_x = np.min(points[:, 0]), np.max(points[:, 0])
    min_y, max_y = np.min(points[:, 1]), np.max(points[:, 1])

    pt1 = 0.5 * (min_x + max_x), 2*max_y - min_y
    pt2 = 2*min_x - max_x, 2*min_y - max_y
    pt3 = 2*max_x - min_x, 2*min_y - max_y

    points = np.array([pt1, pt2, pt3])
    triangle = (0, 1, 2)
    return points, triangle

def bowyer_watson(points_list):
    points_list = np.random.rand(30, 2)  # 30 random points in 2-D

    tri = Triangulation()

    super_triangle = get_super_triangle(points_list)
    for point in super_triangle[0]:
        tri.add_point(point)
    tri.add_triangle(super_triangle[1])

    for point in points_list:
        bad_triangles = []
        point_idx = tri.add_point(point)
        for triangle in tri.triangles:
            center, radius = calc_circumcircle(tri.points[list(triangle)])
            vec = point[0] - center[0], point[1] - center[1]
            if calc_len(vec) < radius:
                bad_triangles.append(triangle)

        polygon = []
        for triangle in bad_triangles:
            triangle_edges = get_triangle_edges(triangle)
            for edge in triangle_edges:
                other_bad_edges = [edge for other_triangle in bad_triangles if other_triangle != triangle for edge in get_triangle_edges(other_triangle)]
                if edge not in other_bad_edges: # edges
                    polygon.append(edge)

        for triangle in bad_triangles:
            tri.remove_triangle(triangle)

        for edge in polygon:
            tri.add_triangle((edge[0], edge[1], point_idx))

    for triangle in tri.triangles.copy():
        if any([idx < 3 for idx in triangle]):
            tri.remove_triangle(triangle)

    print(tri)
    tri.points = tri.points[3:]
    tri.triangles = set([(triangle[0]-3, triangle[1]-3, triangle[2]-3) for triangle in tri.triangles])

    return tri


if __name__ == '__main__':
    points_list = np.random.rand(50, 2)
    tri = bowyer_watson(points_list)
    tri.display()

    print('done')