from config import *
import main
import pygame
import json
import tkinter
from entities.graphcomponents import Vertex, Edge, GameGraph

class GraphCreatorGame(main.Game):
    def __init__(self) -> None:
        super().__init__()

        self.save_button = main.Button('Save', 50, 50, 100, 50)
        self.vertex_count = 0

    def handle_events(self):
        self.events = pygame.event.get()
        for event in self.events:
            self.hovered_vertex = None
            for vertex in self.g.nodes:
                if vertex.hovered:
                    self.hovered_vertex = vertex
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.origin_vertex = self.hovered_vertex
            if event.type == pygame.MOUSEBUTTONUP:
                if self.hovered_vertex is not None:
                    new_edge = Edge(self.origin_vertex, self.hovered_vertex)
                    self.g.add_edge(self.origin_vertex, self.hovered_vertex)
                    self.g.edge_objects.append(new_edge)
                elif self.save_button.hovered:
                    self.export_graph()
                else:
                    x, y = pygame.mouse.get_pos()
                    new_vertex = Vertex(x, y, id=self.vertex_count)
                    new_vertex.graph = self.g
                    self.g.add_node(new_vertex)
                    self.vertex_count += 1

            if event.type == pygame.QUIT:
                self.running = False

    def render(self) -> None:
        self.DISPLAY_SURF.fill(pygame.color.Color("white"))
        for edge in self.g.edge_objects:
            edge.render(self.DISPLAY_SURF)
        for vertex in self.g.nodes:
            vertex.render(self.DISPLAY_SURF)
        
        self.save_button.update()
        self.save_button.render(self.DISPLAY_SURF)

        pygame.display.update()

    def export_graph(self):
        vertices_list = []
        edges_list = []
        nodes_list = list(self.g.nodes)
        for i in range(len(nodes_list)):
            vertex = nodes_list[i]
            save_position_x = vertex.x - GRAPH_CENTER_X
            save_position_y = vertex.y - GRAPH_CENTER_Y
            vertices_list.append({'id': vertex.id, 'position':(save_position_x, save_position_y)})
        for edge in self.g.edge_objects:
            edges_list.append({'origin': edge.origin.id, 'destination': edge.destination.id})
        graph_dict = {'vertices': vertices_list, 'edges': edges_list}

        tkinter.Tk().withdraw()
        f = tkinter.filedialog.asksaveasfile(initialfile='untitled.json', initialdir=USER_GRAPHS_PATH, mode='w', defaultextension=".json")
        try:
            f.write(json.dumps(graph_dict))
            f.close()
        except:
            print("Couldn't write to file")

if __name__=="__main__":
    # call the main function
    game = GraphCreatorGame()
    while game.running:
        game.game_loop()
                
