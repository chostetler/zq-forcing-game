from telnetlib import GA
import pygame
import networkx as nx
import json
import main
import math
from entities.particles import ClickParticle
from config import *
from state.states import GameState, ActionState

class Edge:
    def __init__(self, origin, destination):
        self.origin: Vertex = origin
        self.destination: Vertex = destination
        self.hovered = False
        self.visible = True
        self.animation_counter = 0

    def render(self, surface):
        if self.hovered:
            pass
        if self.visible:
            self.render_color = 'black'
            self.render_width = 2
            if self.graph.game.action_state == ActionState.RULE_3_BLUE:
                if self.origin.component_hovered or self.destination.component_hovered:
                    self.render_color = RULE_3_HOVER_COLOR
                elif self.origin.component_selected or self.destination.component_selected:
                    self.render_color = RULE_3_SELECTED_COLOR
            if self.is_forceable:
                self.green_value = 100 + 100 * math.sin(2*math.pi*self.animation_counter/700)
                self.render_color = pygame.color.Color(0, round(self.green_value), 255)
                self.render_width = 4
                if self.hovered:
                    self.render_color = 'red'

            pygame.draw.line(surface, self.render_color, (self.origin.x, self.origin.y), (self.destination.x, self.destination.y), self.render_width)


    def link_graph(self, graph):
        self.graph: GameGraph = graph

    def update(self, dt=60):
        self.is_forceable = self.origin.can_force(self.destination) or self.destination.can_force(self.origin)
        self.animation_counter += dt
        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_path_distance = math.sqrt((self.origin.x-mouse_x)**2 + (self.origin.y-mouse_y)**2) + math.sqrt((self.destination.x-mouse_x)**2 + (self.destination.y-mouse_y)**2)
        direct_distance = math.sqrt((self.origin.x-self.destination.x)**2 + (self.origin.y-self.destination.y)**2)
        if mouse_path_distance <= direct_distance*1.02:
            self.hovered = True
        else:
            self.hovered = False
        

class Vertex:
    highlight_color = RULE_1_HOVER_COLOR

    def __init__(self, x, y, radius=DEFAULT_VERTEX_RADIUS, is_filled=False, id=None):
        self.x = x
        self.y = y
        self.coordinates = pygame
        self.radius = radius
        self.is_filled = is_filled

        self.id = id

        self.linewidth = 4
        self.rect = pygame.Rect(x-radius, y-radius, radius*2, radius*2)
        self.hovered = False
        self.highlighted = False
        self.visible = True

        self.has_forced = False
        self.force_time = 0

        self.border_color = 'black'
        self.label_font = pygame.font.SysFont("Arial", 20)

    def render(self, surface: pygame.Surface):
        if not self.visible: return None
        if self.is_filled:
            self.color = FILLED_COLOR
        else:
            self.color = EMPTY_COLOR
        pygame.draw.circle(surface, self.color, (self.x, self.y), self.radius, 0)

        self.border_color = pygame.color.Color('black')
        if self.graph.game.action_state == ActionState.RULE_1:
            if self.hovered and not self.is_filled:
                self.border_color = RULE_1_HOVER_COLOR
        elif self.graph.game.action_state == ActionState.RULE_3_BLUE:
            if self.component_hovered:
                self.border_color = RULE_3_HOVER_COLOR
            elif self.component_selected:
                self.border_color = RULE_3_SELECTED_COLOR

        if RENDER_VERTEX_LABELS:
            label_text = self.label_font.render(str(self.id), True, 'black')
            surface.blit(label_text, (self.x+self.radius*.7, self.y+self.radius*.7))
        
        if RENDER_VERTEX_TOKENS and self in self.graph.game.token_vertices:
            token_image = pygame.transform.scale(pygame.image.load(IMAGES_PATH / 'token.png'), (15, 15))
            surface.blit(token_image, token_image.get_rect(center=(self.x, self.y + DEFAULT_VERTEX_RADIUS + 10)))
            # token_image.blit(surface, token_image.get_rect(center=(self.x, self.y)))

        pygame.draw.circle(surface, self.border_color, (self.x, self.y), self.radius, self.linewidth)

    def link_graph(self, graph):
        self.graph: GameGraph = graph

    def turn_blue(self):
        if self.is_filled: return None
        self.force_time = pygame.time.get_ticks() + TIME_BETWEEN_AUTOFORCE
        bubble_sound = pygame.mixer.Sound(SOUNDS_PATH / 'bubble.wav')
        bubble_sound.play()
        self.is_filled = True
        particle = ClickParticle(self.x, self.y, FILLED_COLOR, self.radius)
        self.graph.game.particles.append(particle)

    def update(self, dt=60):
        if self.is_filled and pygame.time.get_ticks() >= self.force_time and not self.has_forced and AUTOFORCE_ENABLED:
            self.graph.do_forces()
            self.has_forced = True
        self.hovered = self.rect.collidepoint(pygame.mouse.get_pos())
        self.component_hovered = self in self.graph.hovered_connected_component
        self.component_selected = self.graph.connected_component(self) in self.graph.selected_connected_components

    def can_force(self, destination):
        return self.graph.can_force(self, destination)
class GameGraph(nx.Graph):
    def __init__(self, filename=None, parent_game=None):
        super().__init__()
        self.game: 'main.Game' = parent_game
        self.edge_objects = []
        if filename is not None:
            self.load_from_file(filename)
        self.selected_connected_components = set()
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
                vertex = Vertex(x, y, 20, id=v['id'])
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

    def component_is_hovered(self, vertex):
        if vertex not in self.nodes: return False

    def update(self, dt=0):
        self.white_vertices = [vertex for vertex in self.nodes if not vertex.is_filled]
        self.filled_vertices = [vertex for vertex in self.nodes if vertex.is_filled]
        self.nx_graph: nx.Graph = nx.Graph(self.edges)
        self.connected_components_sets = list(nx.connected_components(nx.induced_subgraph(self.nx_graph, self.white_vertices)))
        self.hovered_connected_component = {}
        for cc in self.connected_components_sets:
            for vertex in cc:
                if vertex.hovered:
                    self.hovered_connected_component = cc
        if self.game.action_state == ActionState.RULE_1:
            self.selected_connected_components = []

    def do_forces(self):
        to_be_forced = []
        for vertex in self.filled_vertices:
            neighbors = [v for v in nx.neighbors(self, vertex) if not v.is_filled]
            if len(neighbors) == 1:
                to_be_forced.append(neighbors[0])
        for vertex in to_be_forced:
            vertex.turn_blue()

    def vertices_in_selected_connected_components(self):
        vertices = []
        for cc in self.selected_connected_components:
            vertices += list(cc)
        return vertices

    def connected_component(self, vertex: Vertex):
        for cc in self.connected_components_sets:
            if vertex in cc:
                return cc
        return None

    def can_force(self, origin: Vertex, destination: Vertex):
        if origin not in self.filled_vertices: return False
        neighbors = [v for v in nx.neighbors(self, origin) if not v.is_filled]
        if len(neighbors) == 1 and destination in neighbors:
            return True



