import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import Delaunay
import pickle
from math import sqrt, acos, pi, atan2
from utils.read_svg import *
from utils.quadtree import *
from utils.helper import *

# TODO:
# efficiency
# script folder
# refactor run?
# obj saving?
# read improvements
# gear min_angle=20 breaks

# RUPPERTS ALGORITHM
class Rupperts:
    def __init__(self, V, S, min_angle=20, max_area=np.inf):
        self.V = np.array(V)
        self.S = np.array(S)
        self.triangulation = Delaunay(V)
        self.min_angle = min_angle
        self.max_area = max_area
        self.vertex_quadtree = None
        self.initialize_algo()

    def initialize_algo(self):
        self.add_bounding_box()
        self.corner_shielding()
        self.update_triangulation()

    def add_bounding_box(self):
        min_x, max_x = np.min(self.V[:, 0]), np.max(self.V[:, 0])
        min_y, max_y = np.min(self.V[:, 1]), np.max(self.V[:, 1])
        k = 0.5
        span_x, span_y = max_x - min_x, max_y - min_y
        bbox = np.array([[min_x - k*span_x, min_y - k*span_y], [min_x - k*span_x, max_y + k*span_y], [max_x + k*span_x, max_y + k*span_y], [max_x + k*span_x, min_y - k*span_y]])
        self.V = np.append(self.V, bbox, axis=0)
        self.S = np.append(self.S, [[len(self.V)-4, len(self.V)-3], [len(self.V)-3, len(self.V)-2], [len(self.V)-2, len(self.V)-1], [len(self.V)-1, len(self.V)-4]], axis=0)
        self.vertex_quadtree = QuadTree(Rectangle(bbox[0][0], bbox[0][1], bbox[2][0]-bbox[0][0], bbox[2][1]-bbox[0][1]))

    def corner_shielding(self):
        # for each vertex, check if angle btw segments is too small
        # if so, calculate local feature size by finding smallest distance to other vertex
        # insert vertices to segments at lfs radius
        
        for vert_idx, vertex in enumerate(self.V):
            segments = self.S[np.where((self.S == vert_idx).any(axis=1))]
            if len(segments) < 2:
                continue
            # lfs - local feature size
            lfs, shortest_seg = np.inf, None
            angles = []
            for seg in segments:
                vec = self.V[seg[1]] - vertex if (seg[0] == vert_idx) else self.V[seg[0]] - vertex
                vec_len = calc_len(vec)
                if vec_len < lfs:
                    lfs = vec_len
                    shortest_seg = seg
                # get 360 angle
                angles.append(atan2(vec[1], vec[0]) * 180 / pi)
            min_angle_diff = np.min(np.diff(sorted(angles)))
            if min_angle_diff < 3*self.min_angle:
                for seg in segments:
                    if shortest_seg is not None and np.allclose(seg, shortest_seg):
                        continue
                    seg_endpoint = self.V[seg[0]] if seg[1] == vert_idx else self.V[seg[1]]
                    new_point = vertex + lfs * (seg_endpoint - vertex) / calc_len(seg_endpoint - vertex)
                    self.split_seg(seg, new_vertex=new_point)
    
    def update_triangulation(self):
        self.triangulation = Delaunay(self.V)

    def get_seg_index(self, seg):
        try:
            return np.where((self.S == seg).all(axis=1))[0][0]
        except:
            return None

    def get_vert_index(self, vert):
        try:
            return np.where((self.V == vert).all(axis=1))[0][0]
        except:
            return None

    def fix_encroached(self, segments=None, vertices=None):
        # Note: does not update triangulation
        fixed = True
        segments = self.S if segments is None else segments
        vertices = self.V if vertices is None else vertices
        segments_to_split = []
        self.vertex_quadtree.clear()
        for vertex in vertices:
            self.vertex_quadtree.insert(Point(vertex[0], vertex[1]))
        for seg in segments:
            center = 0.5 * (self.V[seg[0]] + self.V[seg[1]])
            radius = calc_len(self.V[seg[0]] - self.V[seg[1]]) / 2
            nearby_points = self.vertex_quadtree.query(Rectangle(center[0]-radius, center[1]-radius, 2*radius, 2*radius))
            for vertex_point in nearby_points:
                vec = vertex_point.x - center[0], vertex_point.y - center[1]
                if vec[0]**2 + vec[1]**2 < radius ** 2 - 1e-6: # if vertex is encroaching
                    segments_to_split.append(seg)    # recursively check new segments
                    fixed = False
                    break

        if not fixed:
            for seg in segments_to_split:
                self.split_seg(seg)
            self.fix_encroached()
        return fixed

    def split_seg(self, seg, new_vertex=None):
        if new_vertex is None:
            new_vertex = 0.5 * (self.V[seg[0]] + self.V[seg[1]])
        self.V = np.append(self.V, [new_vertex], axis=0)
        new_segments = [[seg[0], len(self.V)-1], [len(self.V)-1, seg[1]]]
        self.S = np.append(self.S, new_segments, axis=0)
        self.S = np.delete(self.S, self.get_seg_index(seg), axis=0)
        return new_segments

    def get_min_triangle_size(self):
        min_area = np.inf
        for triangle in self.triangulation.simplices:
            area = calc_area(self.V[triangle])
            if area < min_area:
                min_area = area
        return min_area

    def plot(self, title=None, show=True, triangulation=True, vertices=True, highlight_vt_idx=None, highlight_seg_idx=None, ax=None):
        if ax is None:
            fig, ax = plt.subplots()
        ax.set_aspect('equal')
        if vertices:
            ax.scatter(self.V[:, 0], self.V[:, 1], s=6)
        for seg in self.S:
            ax.plot(self.V[seg, 0], self.V[seg, 1], 'r-', linewidth=0.5)
        if triangulation:
            ax.triplot(self.V[:, 0], self.V[:, 1], self.triangulation.simplices, linewidth=1)
        
        # for debugging
        if highlight_vt_idx is not None:
            vertex = self.V[highlight_vt_idx]
            ax.plot(vertex[0], vertex[1], 'yo', markersize=6)
        if highlight_seg_idx is not None:
            segment = self.S[highlight_seg_idx]
            x, y = zip(*self.V[segment])
            ax.plot(x, y, 'c-', markersize=10)
        if title:
            ax.set_title(title)
        if show:
            plt.show()
        return ax

    def __eq__(self, other):
        return np.array_equal(self.V, other.V) and np.array_equal(self.S, other.S)

    def copy(self):
        return Rupperts(self.V.copy(), self.S.copy(), min_angle=self.min_angle)

    def fix_bad_triangles(self):
        if len(self.V) > 2000:
            print('too many triangles, ending recursion')
            return
        fixed = True
        for triangle in self.triangulation.simplices:
            min_angle = get_min_angle(self.V[triangle])
            if min_angle < self.min_angle or calc_area(self.V[triangle]) > self.max_area:
                circumcenter, radius = calc_circumcircle(self.V[triangle])
                circumcenter_idx = len(self.V)                
                if self.fix_encroached(vertices=[circumcenter]):
                    self.V = np.append(self.V, [circumcenter], axis=0)
                fixed = False
                break

        self.update_triangulation()
        if fixed is False:
            self.fix_bad_triangles()

    def run_algo(self):
        print('Running Ruppert\'s Algorithm')
        print('fixing encroached segments...')
        self.fix_encroached()
        self.update_triangulation()
        # self.plot(title='After fixing encroaching segments')
        print('fixing bad triangles...')
        self.fix_bad_triangles()
        # self.plot(title='After fixing bad triangles')
        print('removing outside triangles...')
        final_triangles = self.remove_outside()
        # self.plot(title='After removing outside')
        return final_triangles

    def remove_outside(self):
        deleted_vertices = []
        min_x, max_x = np.min(self.V[:, 0]), np.max(self.V[:, 0])
        min_y, max_y = np.min(self.V[:, 1]), np.max(self.V[:, 1])
        segment_vertices = set([vert_idx for segment in self.S for vert_idx in segment])
        for vert_idx, vertex in enumerate(self.V.copy()):
            if vertex[0] == min_x or vertex[0] == max_x or vertex[1] == min_y or vertex[1] == max_y:
                deleted_vertices.append(vert_idx)
                continue
            if vert_idx in segment_vertices:
                continue
            if point_in_polygon_edges(vertex, self.V[self.S]):
                deleted_vertices.append(vert_idx)
        
        for vert_idx in sorted(deleted_vertices, reverse=True):
            self.V = np.delete(self.V, vert_idx, axis=0)
            self.S = self.S[np.where((self.S != vert_idx).all(axis=1))]
            self.S = np.where(self.S > vert_idx, self.S - 1, self.S)
        
        self.update_triangulation()

        segment_vertices = set([vert_idx for segment in self.S for vert_idx in segment])
        final_triangles = []
        for triangle in self.triangulation.simplices:
            centroid = np.mean(self.V[triangle], axis=0)
            if point_in_polygon_edges(centroid, self.V[self.S]):
                final_triangles.append(triangle)
        
        return final_triangles
    

def save_triangle_mesh(filepath, vertices, faces, boundary_edges):
    with open(filepath, 'wb') as f:
        pickle.dump([vertices, faces, boundary_edges], f)
    print('Saved mesh to', filepath)
