# Mesh Generation and Refinement

This project includes implementations of various mesh generation and refinement algorithms including
- [x] **Computing Delaunay triangulation** using the Bowyer-Watson algorithm (triangulation.py)
- [x] **Quality mesh generation** using Ruppert's algorithm (rupperts.py)
- [x] **Improve mesh uniformity** using Voronoi relaxation or Lloyd's algorithm (lloyds.py)
- [x] **3d mesh generation from scalar fields** using Marching Cubes algorithm (marching_cubes.py)

Also included are some other useful algorithms
- [x] **Polyline simplification** using the Douglas-Peucker algorithm (douglas_peucker.py)

\
The motivation for this project is to generate high quality meshes for use in finite element analysis, computer graphics and other applications. 

## Description
- triangulation.py - triangulates a set of points according to Delaunay algorithm
- rupperts.py - given planar straight line graph (PSLG), generates a minimal mesh with high quality triangles
- lloyds.py - improves mesh uniformity by iteratively moving vertices to the centroid of their Voronoi region
- marching_cubes.py - generates a 2D surface mesh from a scalar function defined over 3d space
- douglas_peucker.py - simplifies a polyline by removing points that are less critical to the shape of the polyline

## Examples
### Ruppert's algorithm
Given an SVG file of the outline of California, we parse the file into a PSLG (left), compute the minimal triangulation using Ruppert's algorithm (middle), and refine it further until all triangles are below a maximum triangle size (right).

![rupperts_example](demos/rupperts_demo.png)


Near the Bay Area, we see that the triangles are smaller than in the rest of the state. This is because the outline of the bay has smaller features and thus needs smaller and more triangles to capture the shape.

### Lloyd's algorithm
Starting with an initial mesh (left) consisting of a random set of points, we apply Lloyd's algorithm to improve the mesh uniformity (right).

![lloyds_example](demos/lloyds_demo.png)

The initial Voronoi and Delaunay diagrams are very irregular, but after a few iterations of Lloyd's algorithm, the triangle uniformity improves significantly.

### Marching Cubes
Given a parametric function for a 3D scalar field, we use the Marching Cubes algorithm to generate a mesh of the surface.

![marching_cubes_example](demos/marching_cubes_demo.png)

The marching cubes algorithm works by dividing the 3D space into cubes and approximating the surface within each cube with a triangle mesh.

## Demos
Run the demos by running the following commands in the root directory of the project:
```
python -m demos.demo_script -all
```