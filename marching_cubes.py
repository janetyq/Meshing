import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mc_tables import *
from math import pi, cos, sin

def plot_vertices(vertices):
    vertices = np.array(vertices)
    x, y, z = vertices[:, 0], vertices[:, 1], vertices[:, 2]
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(x, y, z, c='b', marker='.')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    plt.show()

def plot_mesh(vertices, faces, title='3D Mesh', show_points=False):
    vertices, faces = np.array(vertices), np.array(faces)
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    ax.plot_trisurf(vertices[:, 0], vertices[:, 1], vertices[:, 2], triangles=faces, cmap='viridis')
    if show_points:
        ax.scatter(vertices[:, 0], vertices[:, 1], vertices[:, 2], c='b', marker='.')

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_aspect('equal')
    ax.set_title(title)

    plt.show()

def create_voxel_grid(ranges, res, func):
    coords = np.mgrid[tuple(slice(ranges[i][0], ranges[i][1], res) for i in range(3))]
    voxel_grid = np.vectorize(func)(*coords)
    return voxel_grid

def grid_to_mesh(voxel_grid, resolution, corner_pos):
    vertices = set()
    faces_points = []
    face_normals = []
    X, Y, Z = voxel_grid.shape
    for i in range(X-1):
        for j in range(Y-1):
            for k in range(Z-1):
                # calculate the origin position of the current cube
                base_pos = np.array([(i+0.5)*resolution, (j+0.5)*resolution, (k+0.5)*resolution]) + corner_pos
                # convert cube array to cube configuration index for tables
                cube_index = np.packbits(voxel_grid[i:i+2, j:j+2, k:k+2].transpose(2, 1, 0).ravel()[::-1])[0]
                # triplets of edge indices corresponding to each face
                triangles = TriangleTable[cube_index]
                
                for t in range(0, len(triangles), 3):
                    face = triangles[t:t+3]
                    if face[0] == -1: # no more triangles left
                        break

                    # calculates point locations and normals of each face
                    points = [tuple(edge_positions[edge_idx] * resolution + base_pos) for edge_idx in face]
                    normal = np.cross(np.array(points[1]) - np.array(points[0]), np.array(points[2]) - np.array(points[0]))
                    normal /= np.linalg.norm(normal)

                    faces_points.append(points)
                    face_normals.append(normal/np.linalg.norm(normal))
                    vertices.update(points)
    
    # aggregate all vertices and find corresponding face indexes
    vertices = [list(vertex) for vertex in vertices]
    index_dict = {tuple(vertex): i for i, vertex in enumerate(vertices)}
    faces = [[index_dict[tuple(vertex)] for vertex in f] for f in faces_points]
    return vertices, faces

def marching_cubes(x_range, y_range, z_range, resolution, func):
    voxel_grid = create_voxel_grid((x_range, y_range, z_range), resolution, func)
    vertices, faces = grid_to_mesh(voxel_grid, resolution, np.array([x_range[0], y_range[0], z_range[0]]))
    return vertices, faces


if __name__ == "__main__":
    # MARCHING CUBES DEMO

    # Define a parametric function
    def torus(x, y, z, R=1.2, r=0.6):
        cond1 = R - r < np.sqrt(x**2 + y**2) < R + r
        cond2 = z**2 + (np.sqrt(x**2 + y**2)-R)**2 < r**2
        return cond1 and cond2
    
    def foo(x, y, z):
        # cool surface
        return 0.7*sin(1.7*x+1.2*y) + sin(-y) + 1.5*z > 0

    # Set dimensions
    x_range, y_range, z_range = (-2, 2), (-2, 2), (-2, 2)
    resolution = 0.15

    # Marching Cubes
    vertices, faces = marching_cubes(x_range, y_range, z_range, resolution, foo)

    # Plot result
    plot_mesh(vertices, faces)
    plt.show() 