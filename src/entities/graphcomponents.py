import pygame
import networkx as nx
import json
from entities.particles import ClickParticle
from config import *

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

    def __init__(self, x, y, radius=DEFAULT_VERTEX_RADIUS, is_filled=False):
        self.x = x
        self.y = y
        self.coordinates = pygame
        self.radius = radius
        self.is_filled = is_filled

        self.linewidth = 4
        self.rect = pygame.Rect(x-radius, y-radius, radius*2, radius*2)
        self.hovered = False
        self.highlighted = False

        self.border_color = 'black'

        self.blue_start_time = pygame.time.get_ticks()

    def draw(self, surface):
        if self.is_filled and pygame.time.get_ticks() >= self.blue_start_time:
            self.color = FILLED_COLOR
        else:
            self.color = EMPTY_COLOR
        pygame.draw.circle(surface, self.color, (self.x, self.y), self.radius, 0)
        if self.hovered and not self.is_filled:
            self.border_color = pygame.color.Color('orange')
        else:
            self.border_color = pygame.color.Color('black')
        pygame.draw.circle(surface, self.border_color, (self.x, self.y), self.radius, self.linewidth)

    def link_graph(self, graph):
        self.graph = graph

    def turn_blue(self, time_offset=0):
        try:
            self.is_filled = True
            self.blue_start_time = pygame.time.get_ticks() + time_offset
            for vertex in self.graph.nodes:
                if not vertex.is_filled: continue
                neighbors = [nb for nb in nx.neighbors(self.graph, vertex) if not nb.is_filled]
                if len(neighbors) == 1:
                    neighbors[0].turn_blue(time_offset+150)

            # spawn_particle(ClickParticle(self.x, self.y, FILLED_COLOR, self.radius, time_offset))
        except:
            print("Couldn't turn blue. Did you remember to link_graph()?")

    def update(self, dt=60):
        self.hovered = self.rect.collidepoint(pygame.mouse.get_pos())

class GameGraph(nx.Graph):
    def __init__(self, filename=None):
        super().__init__()
        self.edge_objects = []
        if filename is not None:
            self.load_from_file(filename)
        self.update()

    def induced_subgraph(self, *args):
        graph = nx.Graph(self.edges)
        return graph.induced_subgraph(*args)

    def load_from_file(self, filename):
        with open(filename) as graph_file:
            data = json.load(graph_file)
            vertices_dict = {}
            for v in data['vertices']:
                x = v['position'][0] + GRAPH_CENTER_X
                y = v['position'][1] + GRAPH_CENTER_Y
                vertex = Vertex(x, y, 20)
                vertex.link_graph(self)
                vertices_dict[v['id']] = vertex
                self.add_node(vertex)

            for e in data['edges']:
                origin = vertices_dict[e['origin']]
                destination = vertices_dict[e['destination']]
                edge = Edge(origin, destination)
                edge.link_graph(self)
                self.add_edge(edge.origin, edge.destination)
                self.edge_objects.append(edge)

    def component_is_hovered(self, edge):
        if edge not in self.nodes: return False

    def update(self, dt=0):
        self.white_vertices = [vertex for vertex in self.nodes if not vertex.is_filled]
        self.filled_vertices = [vertex for vertex in self.nodes if vertex.is_filled]
        self.nx_graph: nx.Graph = nx.Graph(self.edges)
        self.connected_components_sets = list(nx.connected_components(nx.induced_subgraph(self.nx_graph, self.white_vertices)))


