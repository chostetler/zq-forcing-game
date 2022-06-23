import pygame
import math
from config import *

class ClickParticle:
    growth_rate = 50/1000
    max_radius = 40

    alpha_rate = 255/400

    def __init__(self, x, y, base_color=FILLED_COLOR, radius=DEFAULT_VERTEX_RADIUS):
        self.x = x
        self.y = y
        self.color = base_color
        self.base_color = base_color
        self.radius = radius
        self.is_alive = True
        self.alpha = 255

        self.has_started = False

    def update_pos(self, dt):
        self.radius = self.radius + ClickParticle.growth_rate*dt
        self.alpha = max(0, self.alpha - ClickParticle.alpha_rate*dt)
        self.color.a = math.floor(self.alpha)

        if self.radius > ClickParticle.max_radius or self.alpha <= 0:
            self.is_alive = False

    def render(self, surface):
        width = 5
        self.rect = pygame.Rect(self.x-math.floor(self.radius), self.y-math.floor(self.radius), (self.radius)*2, (self.radius)*2)
        particle_surface = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        pygame.draw.circle(particle_surface, self.color, (self.radius, self.radius), math.ceil(self.radius), width)
        surface.blit(particle_surface, self.rect)
