import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import Voronoi, voronoi_plot_2d, Delaunay
import pickle
from quadtree import *
from helper import *

def lloyds_helper(points, fixed_boundary, grid_quadtree):
    vor = Voronoi(points)
    centroids = {}
    for i in range(len(vor.points)):
        seed_point = vor.points[i]
        region = vor.regions[vor.point_region[i]]
        polygon = [vor.vertices[j] if j >= 0 else seed_point for j in region]
        if len(polygon) < 3:
            continue
        
        min_x, max_x = min([pt[0] for pt in polygon]), max([pt[0] for pt in polygon])
        min_y, max_y = min([pt[1] for pt in polygon]), max([pt[1] for pt in polygon])
        grid_points = grid_quadtree.query(Rectangle(min_x, min_y, max_x - min_x, max_y - min_y))
        grid_points = [grid_point.get() for grid_point in grid_points]
        valid_points = np.array([grid_point for grid_point in grid_points if point_in_polygon_points(grid_point, polygon)])

        if len(valid_points) > 0:
            centroid = np.mean(valid_points, axis=0)
            if i not in fixed_boundary:
                points[i] = centroid

    return points

def lloyds(points, fixed_boundary=None, n=3):
    N = len(points)
    triangulation = Delaunay(points)

    if fixed_boundary is None:
        fixed_boundary = list(set(triangulation.convex_hull.ravel()))

    boundary_points = points[fixed_boundary]
    x_min, x_max = np.min(boundary_points[:, 0]), np.max(boundary_points[:, 0])
    y_min, y_max = np.min(boundary_points[:, 1]), np.max(boundary_points[:, 1])

    x_grid, y_grid = np.meshgrid(np.linspace(x_min, x_max, N), np.linspace(y_min, y_max, N))
    grid_points = np.column_stack((x_grid.ravel(), y_grid.ravel()))
    # only keep points inside triangulation
    grid_points = grid_points[triangulation.find_simplex(grid_points) >= 0]

    grid_quadtree = QuadTree(Rectangle(0, 0, 1, 1))
    for point in grid_points:
        grid_quadtree.insert(Point(point[0], point[1]))

    for i in range(n):
        points = lloyds_helper(points, fixed_boundary, grid_quadtree)
    return points


def plot_voronoi_delaunay_result(initial_vertices, final_vertices, fixed_boundary=None, boundary_edges=None, faces=None):
    fig, axs = plt.subplots(2, 2, figsize=(12, 12))
    fig.suptitle('Lloyd\'s Relaxation Algorithm\n(Before & After)')

    # Voronoi plotting
    vor_initial = Voronoi(initial_vertices)
    voronoi_plot_2d(vor_initial, ax=axs[0, 0], point_size=4)
    axs[0, 0].set_title('Initial Voronoi')
    axs[0, 0].set_aspect('equal')
    if fixed_boundary is not None:
        axs[0, 0].scatter(initial_vertices[fixed_boundary][:,0], initial_vertices[fixed_boundary][:,1], color='k', s=10)

    vor_final = Voronoi(final_vertices)
    voronoi_plot_2d(vor_final, ax=axs[0, 1], point_size=4)
    axs[0, 1].set_title('Final Voronoi')
    axs[0, 1].set_aspect('equal')
    if fixed_boundary is not None:
        axs[0, 1].scatter(final_vertices[fixed_boundary][:,0], final_vertices[fixed_boundary][:,1], color='k', s=10)

    # Delaunay plotting
    initial_faces = Delaunay(initial_vertices).simplices if faces is None else faces
    axs[1, 0].triplot(initial_vertices[:,0], initial_vertices[:,1], initial_faces)
    axs[1, 0].set_title('Initial Triangulation')
    axs[1, 0].set_aspect('equal')
    if boundary_edges is not None:
        for edge in boundary_edges:
            axs[1, 0].plot(initial_vertices[edge][:,0], initial_vertices[edge][:,1], color='k')

    final_faces = Delaunay(final_vertices).simplices if faces is None else faces
    axs[1, 1].triplot(final_vertices[:,0], final_vertices[:,1], final_faces)
    axs[1, 1].set_title('Final Triangulation')
    axs[1, 1].set_aspect('equal')
    if boundary_edges is not None:
        for edge in boundary_edges:
            axs[1, 1].plot(initial_vertices[edge][:,0], initial_vertices[edge][:,1], color='k')

    plt.show()

def generate_rectangle_demo(N):
    vertices = np.random.rand(N, 2)
    N_e = int(np.sqrt(N)) + 1
    edges = np.linspace(0, 1, N_e)
    edge_vertices = np.vstack([
        np.column_stack((np.zeros(N_e), edges)),
        np.column_stack((np.ones(N_e), edges)),
        np.column_stack((edges[1:-1], np.zeros(N_e-2))),
        np.column_stack((edges[1:-1], np.ones(N_e-2)))
    ])
    vertices = np.vstack([vertices, edge_vertices])
    fixed_boundary = list(range(N, N + 4*(N_e-1)))
    return vertices, fixed_boundary

if __name__ == '__main__':
    # Create random points
    vertices, fixed_boundary = generate_rectangle_demo(40)

    # with open('lowpoly_california_mesh.pkl', 'rb') as f:
    #     vertices, faces, boundary_edges = pickle.load(f)

    # fixed_boundary = list(set([edge[0] for edge in boundary_edges] + [edge[1] for edge in boundary_edges]))

    # Run Lloyd's algorithm
    initial_vertices = vertices.copy()
    vertices = lloyds(vertices, fixed_boundary, n=10)


    plot_voronoi_delaunay_result(initial_vertices, vertices)
    # plot_voronoi_delaunay_result(initial_vertices, vertices, fixed_boundary, boundary_edges, faces)

    # Pickle dump
    # with open('test_vertices.pkl', 'wb') as f:
    #     pickle.dump(vertices, f)


    print('lloyds.py done')