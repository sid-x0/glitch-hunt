import pygame
import random
import math
from PIL import Image
import numpy as np

# --- Load image ---
img = Image.open("mount_fuji.jpg")
img = img.resize((800, 600))
arr = np.array(img)
background_surface = pygame.surfarray.make_surface(arr.transpose(1,0,2))

# --- Draw asymmetric petal function ---
def draw_petal(surface, color, x, y, size, alpha, rotation):
    w, h = size, size*1.8
    points = [
        (0.5*w, 0),              # top middle
        (1.1*w, 0.3*h),          # upper right protrusion
        (0.7*w, h),              # bottom right
        (0.3*w, h),              # bottom left
        (-0.1*w, 0.3*h)          # upper left protrusion
    ]
    # Rotate points around center
    rad = math.radians(rotation)
    rotated_points = []
    cx, cy = w/2, h/2
    for px, py in points:
        dx, dy = px - cx, py - cy
        rx = dx*math.cos(rad) - dy*math.sin(rad) + cx
        ry = dx*math.sin(rad) + dy*math.cos(rad) + cy
        rotated_points.append((rx + x, ry + y))
    # Draw with alpha
    petal_surface = pygame.Surface((800, 600), pygame.SRCALPHA)
    pygame.draw.polygon(petal_surface, (*color, int(alpha)), rotated_points)
    surface.blit(petal_surface, (0,0))

# --- Petal class ---
class Petal:
    def __init__(self, tree_area_index, tree_area):
        x_min, x_max, y_min, y_max = tree_area
        self.base_x = random.randint(x_min, x_max)
        self.y = random.randint(y_min, y_max)
        self.dy = random.uniform(1, 3)
        self.size = random.randint(4, 7)  # smaller size
        self.alpha = random.randint(180, 255)  # initial transparency
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-2, 2)
        # Sway
        self.sway_amplitude = random.uniform(15, 35)
        self.sway_frequency = random.uniform(0.01, 0.03)
        self.phase = random.uniform(0, 2*math.pi)
        # Color
        if tree_area_index == 0:
            self.color = (255, 182, 193)  # pink
        else:
            self.color = (255, 255, 255)  # white

    def move(self):
        self.y += self.dy
        self.base_x += 0  # can add wind effect if needed
        self.x = self.base_x + self.sway_amplitude * math.sin(self.phase)
        self.phase += self.sway_frequency
        self.rotation += self.rotation_speed
        # Fade
        self.alpha -= 0.3
        if self.alpha < 0:
            self.alpha = 0

# --- Pygame setup ---
pygame.init()
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Mount Fuji Blossoms")
clock = pygame.time.Clock()

# Tree areas (click to spawn petals)
tree_areas = [
    (0, 266, 0, 300),    # Left tree
    (500, 650, 170, 350),# Right tree
    (665, 800, 0, 100)   # Top-right compartment
]

petals = []

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            for idx, tree_area in enumerate(tree_areas):
                x_min, x_max, y_min, y_max = tree_area
                if x_min <= mx <= x_max and y_min <= my <= y_max:
                    for _ in range(10):
                        petals.append(Petal(idx, tree_area))
                    break

    screen.blit(background_surface, (0,0))

    for petal in petals[:]:
        petal.move()
        draw_petal(screen, petal.color, petal.x, petal.y, petal.size, petal.alpha, petal.rotation)
        if petal.y > screen_height or petal.alpha <= 0:
            petals.remove(petal)

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
