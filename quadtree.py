import random
import sys

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def draw(self, screen, color=(255, 255, 255), radius=2):
        pygame.draw.circle(screen, color, (self.x, self.y), radius, radius)

    def distance(self, other):
        return ((self.x - other.x)**2 + (self.y - other.y)**2)**0.5
    
    def get(self):
        return self.x, self.y


class Rectangle:
    def __init__(self, x, y, w, h):
        # (x, y) is corner of rectangle
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def contains_point(self, point):
        return (point.x >= self.x and point.x <= self.x + self.w and \
                point.y >= self.y and point.y <= self.y + self.h)

    def intersects(self, range):
        return not (range.x > self.x + self.w or range.x + range.w < self.x or \
                    range.y > self.y + self.h or range.y + range.h < self.y)

    def draw(self, screen, color=(255, 255, 255), width=1):
        pygame.draw.rect(screen, color, (self.x, self.y, self.w, self.h), width)


class QuadTree:
    def __init__(self, boundary, capacity=4):
        self.boundary = boundary
        self.capacity = capacity
        self.points = []
        self.children = []

    def insert(self, point):
        if not self.boundary.contains_point(point):
            return False
        
        if len(self.points) < self.capacity:
            self.points.append(point)
            return True
        else:
            if self.children == []:
                self.subdivide()

            for child in self.children:
                if child.insert(point):
                    return True
    
    def subdivide(self):
        rect1 = Rectangle(self.boundary.x, self.boundary.y, self.boundary.w/2, self.boundary.h/2)
        self.children.append(QuadTree(rect1, self.capacity))
        rect2 = Rectangle(self.boundary.x, self.boundary.y + self.boundary.h/2, self.boundary.w/2, self.boundary.h/2)
        self.children.append(QuadTree(rect2, self.capacity))
        rect3 = Rectangle(self.boundary.x + self.boundary.w/2, self.boundary.y, self.boundary.w/2, self.boundary.h/2)
        self.children.append(QuadTree(rect3, self.capacity))
        rect4 = Rectangle(self.boundary.x + self.boundary.w/2, self.boundary.y + self.boundary.h/2, self.boundary.w/2, self.boundary.h/2)
        self.children.append(QuadTree(rect4, self.capacity))

    def query(self, query_range):
        points = []
        if not self.boundary.intersects(query_range):
            return points
        else:
            for p in self.points:
                if query_range.contains_point(p):
                    points.append(p)
            for child in self.children:
                points += child.query(query_range)
        return points

    def remove(self, point):
        if not self.boundary.contains_point(point):
            return False
        else:
            for self_point in self.points:
                if point.x == self_point.x and point.y == self_point.y:
                    self.points.remove(self_point)
                    return True
            else:
                for child in self.children:
                    if child.remove(point):
                        return True
                return False
    
    def find_nearest(self, point):
        nearest_distance = float('inf')
        if not self.boundary.contains_point(point):
            return None
        else:
            nearest_point = None
            for other_point in self.points:
                distance = point.distance(other_point)
                if distance < nearest_distance:
                    nearest_distance = distance
                    nearest_point = other_point
            for child in self.children:
                nearest_child_point = child.find_nearest(point)
                if nearest_child_point is not None:
                    distance = point.distance(nearest_child_point)
                    if distance < nearest_distance:
                        nearest_distance = distance
                        nearest_point = nearest_child_point
            return nearest_point

    def clear(self):
        self.points = []
        self.children = []

    def draw(self, screen):
        self.boundary.draw(screen)
        for child in self.children:
            child.draw(screen)
    


        


if __name__ == '__main__':
    width, height = 800, 600

    boundary = Rectangle(0, 0, width, height)
    quadtree = QuadTree(boundary, 4)
    
    points = [Point(random.uniform(0, width), random.uniform(0, height)) for i in range(100)]
    for p in points:
        quadtree.insert(p)

    import pygame
    pygame.init()
    screen = pygame.display.set_mode((width, height))
    black = (0, 0, 0)
    red = (255, 0, 0)
    blue = (0, 0, 255)
    green = (0, 255, 0)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    points = []
                    quadtree = QuadTree(boundary, 4)

        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_buttons = pygame.mouse.get_pressed()
        if mouse_buttons[0]:
            point = Point(mouse_x+random.uniform(-5, 5), mouse_y+random.uniform(-5, 5))
            points.append(point)
            quadtree.insert(point)
            pygame.time.delay(20)
        
        
        query_range = Rectangle(mouse_x-50, mouse_y-50, 100, 100)

        screen.fill(black)
        quadtree.draw(screen)
        for i in range(len(points)):
            points[i].draw(screen, color=red)

        query_range.draw(screen, color=green, width=2)
        range_points = quadtree.query(query_range)
        for i in range(len(range_points)):
            range_points[i].draw(screen, color=blue, radius=3)
        
        pygame.display.flip()

    # Quit pygame
    pygame.quit()
