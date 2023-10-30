import pickle
import argparse
from marching_cubes import *
from lloyds import *
from rupperts import *
from triangulation import *

# Run from project directory with `python -m demos.demos_script -all`

parser = argparse.ArgumentParser(description="Demo script for meshing algorithms")
parser.add_argument('-a', '--all', action='store_true', help='Run all demos')
parser.add_argument('-r', '--rupperts', action='store_true', help='Run Ruppert\'s Algorithm demo')
parser.add_argument('-l', '--lloyds', action='store_true', help='Run Lloyd\'s Algorithm demo')
parser.add_argument('-mc', '--marching', action='store_true', help='Run Marching Cubes demo')
parser.add_argument('-t', '--triangulation', action='store_true', help='Run Triangulation demo')

args = parser.parse_args()

if args.all:
    RUPPERTS_DEMO = True
    LLOYDS_DEMO = True
    MARCHING_CUBES_DEMO = True
    TRIANGULATION_DEMO = True
else:
    RUPPERTS_DEMO = args.rupperts
    LLOYDS_DEMO = args.lloyds
    MARCHING_CUBES_DEMO = args.marching
    TRIANGULATION_DEMO = args.triangulation

######################################
###### RUPPERT'S ALGORITHM DEMO ######
######################################

if RUPPERTS_DEMO:
    print('\nRuppert\'s Algorithm Demo')

    # LOAD Planar Straight Line Graph (PSLG) OR Scalar Vector Graphics (SVG)
    #   V - vertices
    #   S - segments - list of pairs of vertex indices
    #   epsilon - parameter for path simplification (Douglas-Peucker), higher = more simplification
    #   min_area - minimum area of polygon to include in PSLG

    demo_type = 'SVG'
    if demo_type == 'PSLG':
        # PSLG example
        with open('mesh_files/pslg_doubleslit.pkl', 'rb') as f:
            V, S = pickle.load(f)
    elif demo_type == 'SVG':
        # SVG example
        V, S = read_and_process_svg('mesh_files/outline-ca.svg', epsilon=10, min_area=10000)
        print('Number of initial vertices:', len(V))

    # RUN Ruppert's Algorithm
    #  min_angle - minimum angle of triangles in final triangulation
    #  max_area - maximum area of triangles in final triangulation
    #  triangles - list of triples of vertex indices of faces in final triangulation
    rupperts = Rupperts(V, S, min_angle=20, max_area=float('inf'))
    triangles = rupperts.run_algo()
    print('Number of triangles:', len(triangles))

    # PLOT RESULTS
    fig, axs = plt.subplots(1, 2, figsize=(12, 6))
    fig.suptitle('Ruppert\'s Algorithm for Triangulation')
    rupperts.plot(title='Initial PSLG', show=False, triangulation=False, vertices=False, ax=axs[0])
    rupperts.plot(title='Final Triangulation', show=False, triangulation=False, ax=axs[1])
    axs[1].triplot(rupperts.V[:, 0], rupperts.V[:, 1], triangles)
    axs[0].invert_yaxis()
    axs[1].invert_yaxis()
    plt.show()

    # SAVE RESULTS
    # save_triangle_mesh('demo_mesh.pkl', rupperts.V, triangles, rupperts.S)


######################################
####### LLOYD'S ALGORITHM DEMO #######
######################################

if LLOYDS_DEMO:
    print('\nLloyd\'s Algorithm Demo')
    # Generates points in a rectangle
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

    demo_type = 'rectangle'
    if demo_type == 'rectangle':
        # Create random points
        vertices, fixed_boundary = generate_rectangle_demo(40)
    elif demo_type == 'california':
        # Load mesh
        with open('lowpoly_california_mesh.pkl', 'rb') as f:
            vertices, faces, boundary_edges = pickle.load(f)
        fixed_boundary = list(set([edge[0] for edge in boundary_edges] + [edge[1] for edge in boundary_edges]))

    # Run Lloyd's algorithm
    initial_vertices = vertices.copy()
    vertices = lloyds(vertices, fixed_boundary, n=10)

    plot_voronoi_delaunay_result(initial_vertices, vertices)

    # Pickle dump
    # with open('test_vertices.pkl', 'wb') as f:
    #     pickle.dump(vertices, f)

######################################
######## MARCHING CUBES DEMO #########
######################################

if MARCHING_CUBES_DEMO:
    print('\nMarching Cubes Demo')

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
    vertices, faces = marching_cubes(x_range, y_range, z_range, resolution, torus)

    # Plot result
    plot_mesh(vertices, faces, title='Donut mesh generated with Marching Cubes')
    plt.show() 

######################################
######## TRIANGULATION DEMO ##########
######################################

if TRIANGULATION_DEMO:
    print('\nBowyer-Watson Triangulation Demo')
    points_list = np.random.rand(50, 2)
    tri = bowyer_watson(points_list)
    tri.display()
