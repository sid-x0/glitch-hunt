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
    rad = math.radians(rotation)
    rotated_points = []
    cx, cy = w/2, h/2
    for px, py in points:
        dx, dy = px - cx, py - cy
        rx = dx*math.cos(rad) - dy*math.sin(rad) + cx
        ry = dx*math.sin(rad) + dy*math.cos(rad) + cy
        rotated_points.append((rx + x, ry + y))
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
        self.size = random.randint(4, 7)
        self.alpha = random.randint(180, 255)
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-2, 2)
        self.sway_amplitude = random.uniform(15, 35)
        self.sway_frequency = random.uniform(0.01, 0.03)
        self.phase = random.uniform(0, 2*math.pi)
        if tree_area_index == 0:
            self.color = (255, 182, 193)  # pink
        else:
            self.color = (255, 255, 255)  # white

    def move(self):
        self.y += self.dy
        self.x = self.base_x + self.sway_amplitude * math.sin(self.phase)
        self.phase += self.sway_frequency
        self.rotation += self.rotation_speed
        self.alpha -= 0.3
        if self.alpha < 0:
            self.alpha = 0

# --- Lava particle class ---
class LavaParticle:
    def __init__(self, x, y):
        self.x = x + random.randint(-5, 5)
        self.y = y
        self.dy = random.uniform(3, 6)
        self.dx = random.uniform(-1, 1)
        self.size = random.randint(4, 8)
        self.color = (255, 50, 0)
        self.alpha = 255

    def move(self):
        self.x += self.dx
        self.y += self.dy
        self.alpha -= 2
        if self.alpha < 0:
            self.alpha = 0

# --- Pygame setup ---
pygame.init()
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Interactive Mount Fuji")
clock = pygame.time.Clock()

# Tree areas
tree_areas = [
    (0, 266, 0, 300),    # Left tree
    (500, 650, 170, 350),# Right tree
    (665, 800, 0, 100)   # Top-right compartment
]

# Volcano area for click detection
# Clickable area for volcano eruption (around the tip)
volcano_top_area = (390, 440, 260, 300)  # x_min, x_max, y_min, y_max
  # x_min, x_max, y_min, y_max

# Fixed volcano tip coordinates (center of image)
volcano_tip_x = 415
volcano_tip_y = 280

petals = []
lava_particles = []

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            # Check trees
            clicked_tree = False
            for idx, tree_area in enumerate(tree_areas):
                x_min, x_max, y_min, y_max = tree_area
                if x_min <= mx <= x_max and y_min <= my <= y_max:
                    for _ in range(10):
                        petals.append(Petal(idx, tree_area))
                    clicked_tree = True
                    break
            # Check volcano
            x_min, x_max, y_min, y_max = volcano_top_area
            if not clicked_tree and x_min <= mx <= x_max and y_min <= my <= y_max:
                for _ in range(20):
                    lava_particles.append(LavaParticle(volcano_tip_x, volcano_tip_y))

    screen.blit(background_surface, (0,0))

    # Update and draw petals
    for petal in petals[:]:
        petal.move()
        draw_petal(screen, petal.color, petal.x, petal.y, petal.size, petal.alpha, petal.rotation)
        if petal.y > screen_height or petal.alpha <= 0:
            petals.remove(petal)

    # Update and draw lava particles
    for particle in lava_particles[:]:
        particle.move()
        lava_surf = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        pygame.draw.circle(lava_surf, (*particle.color, int(particle.alpha)), (int(particle.x), int(particle.y)), particle.size)
        screen.blit(lava_surf, (0,0))
        if particle.y > screen_height or particle.alpha <= 0:
            lava_particles.remove(particle)

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
