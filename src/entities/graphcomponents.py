import pygame
import networkx as nx
from entities.particles import ClickParticle

class Edge:
    def __init__(self, origin, destination):
        self.origin = origin
        self.destination = destination
        self.hovered = False

    def draw(self, surface):
        if self.hovered:
            pass
        pygame.draw.line(surface, pygame.color.Color('black'), (self.origin.x, self.origin.y), (self.destination.x, self.destination.y))
        pass

    def link_graph(self, graph):
        self.graph = graph

    def update(self, dt=60):
        pass

class Vertex:
    highlight_color = pygame.Color('orange')

    def __init__(self, x, y, radius=20, is_blue=False):
        self.x = x
        self.y = y
        self.coordinates = pygame
        self.radius = radius
        self.is_blue = is_blue

        self.linewidth = 4
        self.rect = pygame.Rect(x-radius, y-radius, radius*2, radius*2)
        self.hovered = False
        self.highlighted = False

        self.border_color = 'black'

        self.blue_start_time = pygame.time.get_ticks()

    def draw(self, surface):
        if self.is_blue and pygame.time.get_ticks() >= self.blue_start_time:
            self.color = pygame.color.Color('cyan')
        else:
            self.color = pygame.color.Color('white')
        pygame.draw.circle(surface, self.color, (self.x, self.y), self.radius, 0)
        if self.hovered and not self.is_blue:
            self.border_color = pygame.color.Color('orange')
        else:
            self.border_color = pygame.color.Color('black')
        pygame.draw.circle(surface, self.border_color, (self.x, self.y), self.radius, self.linewidth)

    def link_graph(self, graph):
        self.graph = graph

    def turn_blue(self, time_offset=0):
        try:
            self.is_blue = True
            self.blue_start_time = pygame.time.get_ticks() + time_offset
            for vertex in self.graph.nodes:
                if not vertex.is_blue: continue
                neighbors = [nb for nb in nx.neighbors(self.graph, vertex) if not nb.is_blue]
                if len(neighbors) == 1:
                    neighbors[0].turn_blue(time_offset+150)

            # spawn_particle(ClickParticle(self.x, self.y, pygame.color.Color('cyan'), self.radius, time_offset))
        except:
            print("Couldn't turn blue. Did you remember to link_graph()?")

    def update(self, dt=60):
        self.hovered = self.rect.collidepoint(pygame.mouse.get_pos())
