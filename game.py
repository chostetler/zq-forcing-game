# import the pygame module, so you can use it
import enum
import pygame
import networkx as nx
import math
import json
import sys
 
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

    def draw(self, surface):
        if self.hovered and not self.is_blue:
            pygame.draw.circle(surface, Vertex.highlight_color, (self.x, self.y), self.radius+4, 0)
        if self.is_blue:
            self.color = pygame.color.Color('cyan')
        else:
            self.color = pygame.color.Color('white')
        pygame.draw.circle(surface, self.color, (self.x, self.y), self.radius, 0)
        pygame.draw.circle(surface, pygame.color.Color("black"), (self.x, self.y), self.radius, self.linewidth)

    def link_graph(self, graph):
        self.graph = graph

    def turn_blue(self):
        try:
            self.is_blue = True
            neighbors = [nb for nb in nx.neighbors(self.graph, self) if not nb.is_blue]
            if len(neighbors) == 1:
                neighbors[0].turn_blue()

            spawn_particle(ClickParticle(self.x, self.y, pygame.color.Color('cyan'), self.radius))
        except:
            print("Couldn't turn blue. Did you remember to link_graph()?")

class ClickParticle:
    growth_rate = 50/1000
    max_radius = 40

    alpha_rate = 255/400

    def __init__(self, x, y, base_color, radius):
        self.x = x
        self.y = y
        self.color = base_color
        self.base_color = base_color
        self.radius = radius
        self.is_alive = True
        self.alpha = 255

    def update_pos(self, dt):
        self.radius = self.radius + ClickParticle.growth_rate*dt
        self.alpha = max(0, self.alpha - ClickParticle.alpha_rate*dt)
        self.color.a = math.floor(self.alpha)

        if self.radius > ClickParticle.max_radius or self.alpha <= 0:
            self.is_alive = False

    def draw(self, surface):
        width = 5
        self.rect = pygame.Rect(self.x-math.floor(self.radius), self.y-math.floor(self.radius), (self.radius)*2, (self.radius)*2)
        particle_surface = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        # particle_surface.fill(pygame.color.Color('red'))
        pygame.draw.circle(particle_surface, self.color, (self.radius, self.radius), math.ceil(self.radius), width)
        surface.blit(particle_surface, self.rect)




#############################################################

particles = []

def spawn_particle(particle):
    particles.append(particle)

# define a main function
def main():
    WIN_WIDTH = 640
    WIN_HEIGHT = 480
    
    # initialize the pygame module
    pygame.init()
    # load and set the logo
    logo = pygame.image.load("images\logo32x32.png")
    pygame.display.set_icon(logo)
    pygame.display.set_caption("minimal program")
     
    # create a surface on screen 
    DISPLAY_SURF = pygame.display.set_mode((WIN_WIDTH,WIN_HEIGHT))
     
    # define a variable to control the main loop
    running = True

    clock = pygame.time.Clock()
    dt = 0
     
    g = nx.Graph()

    graph_name = 'K_6'
    if len(sys.argv) >= 2:
        graph_name = sys.argv[1]
    else:
        # print('Please input a graph name')
        # graph_name = input()
        graph_name = 'K_6'



    GRAPH_CENTER_X = 200
    GRAPH_CENTER_Y = 200
    edge_objects = []

    with open(sys.path[0] + '/graphs/' + graph_name + '.json') as graph_file:
        data = json.load(graph_file)
        # print(data)

        vertices_dict = {}

        for v in data['vertices']:
            x = v['position'][0] + GRAPH_CENTER_X
            y = v['position'][1] + GRAPH_CENTER_Y
            vertex = Vertex(x, y, 20)
            vertex.link_graph(g)
            vertices_dict[v['id']] = vertex
            g.add_node(vertex)

        for e in data['edges']:
            origin = vertices_dict[e['origin']]
            destination = vertices_dict[e['destination']]
            edge = Edge(origin, destination)
            edge.link_graph(g)
            g.add_edge(edge.origin, edge.destination)
            edge_objects.append(edge)

    tokens = 0
    font = pygame.font.SysFont("Arial", 30)

    # main loop
    while running:
        # event handling, gets all event from the event queue
        for event in pygame.event.get():
            # only do something if the event is of type QUIT
            if event.type == pygame.QUIT:
                # change the value to False, to exit the main loop
                running = False

            if event.type == pygame.MOUSEBUTTONUP:
                for vertex in g.nodes:
                    if vertex.hovered and not vertex.is_blue:
                        tokens += 1
                        vertex.turn_blue()

        DISPLAY_SURF.fill(pygame.color.Color("white"))

        for particle in particles:
            particle.update_pos(dt)
            particle.draw(DISPLAY_SURF)
            if not particle.is_alive:
                particles.remove(particle)
        
        for edge in edge_objects:
            edge.draw(DISPLAY_SURF)
        for vertex in g.nodes:
            vertex.hovered = vertex.rect.collidepoint(pygame.mouse.get_pos())
            vertex.draw(DISPLAY_SURF)

        tokens_surface = font.render('Tokens: '+str(tokens), True, (0,0,0))
        DISPLAY_SURF.blit(tokens_surface, (20, 20))

        if all([vertex.is_blue for vertex in g.nodes]):
            win_text_surface = font.render('All done! You used '+str(tokens)+' tokens.', True, (0,0,0))
            DISPLAY_SURF.blit(win_text_surface, (50, WIN_HEIGHT-100))

        pygame.display.update()
        dt = clock.tick(60)

     
# run the main function only if this module is executed as the main script
# (if you import this as a module then nothing is executed)
if __name__=="__main__":
    # call the main function
    main()