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
        (0.5*w, 0),
        (1.1*w, 0.3*h),
        (0.7*w, h),
        (0.3*w, h),
        (-0.1*w, 0.3*h)
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
        self.color = (255, 182, 193) if tree_area_index == 0 else (255, 255, 255)

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
font = pygame.font.SysFont(None, 30)

# Tree areas
tree_areas = [
    (0, 266, 0, 300),
    (500, 650, 170, 350),
    (665, 800, 0, 100)
]

# Volcano clickable area
volcano_top_area = (390, 440, 260, 300)
volcano_tip_x = 415
volcano_tip_y = 280

# Basket
basket_width = 100
basket_height = 30
basket_x = 350
basket_y = screen_height - basket_height - 10
basket_speed = 7
basket_color = (139, 69, 19)
basket_alive = True

# Game variables
petals = []
lava_particles = []
score = 0

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            clicked_tree = False
            for idx, tree_area in enumerate(tree_areas):
                x_min, x_max, y_min, y_max = tree_area
                if x_min <= mx <= x_max and y_min <= my <= y_max:
                    for _ in range(10):
                        petals.append(Petal(idx, tree_area))
                    clicked_tree = True
                    break
            x_min, x_max, y_min, y_max = volcano_top_area
            if not clicked_tree and x_min <= mx <= x_max and y_min <= my <= y_max:
                for _ in range(20):
                    lava_particles.append(LavaParticle(volcano_tip_x, volcano_tip_y))

    keys = pygame.key.get_pressed()
    if basket_alive:
        if keys[pygame.K_LEFT]:
            basket_x -= basket_speed
        if keys[pygame.K_RIGHT]:
            basket_x += basket_speed
        basket_x = max(0, min(screen_width - basket_width, basket_x))

    screen.blit(background_surface, (0,0))

    # Draw basket
    if basket_alive:
        pygame.draw.rect(screen, basket_color, (basket_x, basket_y, basket_width, basket_height))
    else:
        game_over_text = font.render("Basket destroyed by lava! lol ", True, (255, 0, 0))
        screen.blit(game_over_text, (screen_width//2 - 120, screen_height//2))

    # Update and draw petals
    for petal in petals[:]:
        petal.move()
        draw_petal(screen, petal.color, petal.x, petal.y, petal.size, petal.alpha, petal.rotation)
        petal_rect = pygame.Rect(petal.x, petal.y, petal.size, petal.size)
        basket_rect = pygame.Rect(basket_x, basket_y, basket_width, basket_height)
        if basket_alive and petal_rect.colliderect(basket_rect):
            petals.remove(petal)
            score += 1
        elif petal.y > screen_height or petal.alpha <= 0:
            petals.remove(petal)

    # Update and draw lava particles
    for particle in lava_particles[:]:
        particle.move()
        lava_surf = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        pygame.draw.circle(lava_surf, (*particle.color, int(particle.alpha)), (int(particle.x), int(particle.y)), particle.size)
        screen.blit(lava_surf, (0,0))
        lava_rect = pygame.Rect(particle.x, particle.y, particle.size, particle.size)
        if basket_alive and lava_rect.colliderect(pygame.Rect(basket_x, basket_y, basket_width, basket_height)):
            basket_alive = False
        if particle.y > screen_height or particle.alpha <= 0:
            lava_particles.remove(particle)

    # Display score
    # Display score in sakura pink at the top center
    score_text = font.render(f"Score: {score}", True, (255, 182, 193))
    text_rect = score_text.get_rect(center=(screen_width // 2, 20))  # y=20 from top
    screen.blit(score_text, text_rect)


    pygame.display.flip()
    clock.tick(30)

pygame.quit()
