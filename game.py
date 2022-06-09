# import the pygame module, so you can use it
import enum
import pygame
import networkx as nx
import math
 
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
        if self.hovered:
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
    growth_rate = 400/1000
    max_radius = 40

    def __init__(self, x, y, color, radius):
        self.x = x
        self.y = y
        self.color = color
        self.radius = radius
        self.is_alive = True

    def update_pos(self, dt):
        self.radius = self.radius + ClickParticle.growth_rate*dt
        if self.radius > ClickParticle.max_radius:
            self.is_alive = False

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (self.x, self.y), self.radius, 5)

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
    
    positions = [(round(200+100*math.cos(step*2*math.pi/5)), round(200+100*math.sin(step *2*math.pi/5))) for step in [0, 1, 2, 3, 4]]
    my_vertices = [Vertex(*position) for position in positions]

    my_edges = []
    for i in range(len(my_vertices)):
        for j in range(i+1, len(my_vertices)):
            my_edges.append(Edge(my_vertices[i], my_vertices[j]))

    for vertex in my_vertices:
        vertex.link_graph(g)

    g.add_nodes_from(my_vertices)
    for edge in my_edges:
        g.add_edge(edge.origin, edge.destination)
        edge.link_graph(g)
    print(g)

    # main loop
    while running:
        # event handling, gets all event from the event queue
        for event in pygame.event.get():
            # only do something if the event is of type QUIT
            if event.type == pygame.QUIT:
                # change the value to False, to exit the main loop
                running = False

            if event.type == pygame.MOUSEBUTTONUP:
                for vertex in my_vertices:
                    if vertex.hovered:
                        vertex.turn_blue()

        DISPLAY_SURF.fill(pygame.color.Color("white"))

        for particle in particles:
            particle.update_pos(dt)
            particle.draw(DISPLAY_SURF)
            if not particle.is_alive:
                particles.remove(particle)
        
        for edge in my_edges:
            edge.draw(DISPLAY_SURF)
        for vertex in my_vertices:
            vertex.hovered = vertex.rect.collidepoint(pygame.mouse.get_pos())
            vertex.draw(DISPLAY_SURF)

        pygame.display.update()
        dt = clock.tick(60)

     
# run the main function only if this module is executed as the main script
# (if you import this as a module then nothing is executed)
if __name__=="__main__":
    # call the main function
    main()