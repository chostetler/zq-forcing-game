# import the pygame module, so you can use it
import pygame
import networkx as nx
import math
import json
import tkinter
from pathlib import Path
from tkinter.filedialog import askopenfilename
from enum import Enum
from config import *
from entities.graphcomponents import GameGraph, Vertex, Edge
 
class Button():
    def __init__(self, text, x, y, width, height, font=None, hover_color=(150, 150, 255)):
        self.text = text
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.font = pygame.font.SysFont('Arial', 30)
        self.hover_color = hover_color
        self.draw_color = 'white'
        self.hovered = False
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.surface = pygame.Surface(self.rect.size)

    def update(self, dt=60):
        self.hovered = self.rect.collidepoint(pygame.mouse.get_pos())
        self.draw_color = self.hover_color if self.hovered else 'white'

    def draw(self, surface: pygame.surface.Surface):
        pygame.draw.rect(surface, self.draw_color, self.rect)
        pygame.draw.rect(surface, 'black', self.rect, 4)
        button_text = self.font.render(self.text, True, 'black')
        surface.blit(button_text, (self.x+5, self.y+5))

    def click(self):
        click_sound = pygame.mixer.Sound(SOUNDS_PATH / 'menu-bip.wav')
        click_sound.play()

class ForceArrow:
    def __init__(self, origin: Vertex, destination: Vertex):
        self.origin = origin
        self.destination = destination

    def draw(self, surface: pygame.surface.Surface):
        self.origin_coords = (self.origin.x, self.origin.y)
        self.destination_coords = (self.destination.x, self.destination.y)
        self.center_coords = (self.origin_coords + self.destination_coords) / 2
        self.dy, self.dx = (self.destination_coords - self.origin_coords)

        self.angle = math.atan2(self.dy, self.dx)
        arrow_image = pygame.image.load(IMAGES_PATH / 'force-arrow.png')
        arrow_rotated = pygame.transform.rotate(arrow_image, self.angle)

        arrow_rotated.blit(surface, arrow_rotated.get_rect(center=self.center_coords))

#TODO: The state functionality needs lots of cleaning up. I might redo all this...


class GameState(Enum):
    MENU = 0
    INSTRUCTIONS = 1
    CHOOSE_FILE = 2
    GAME = 3
    GAME_OVER = 4

class ActionState(Enum):
    RULE_1 = 1
    RULE_3_BLUE = 2
    RULE_3_WHITE = 3
    RULE_3_FORCE = 4

#############################################################

particles = []

def spawn_particle(particle):
    particles.append(particle)

# define a main function
def main():
    game_data = {}
    # initialize the pygame module
    pygame.init()
    # load and set the logo
    logo = pygame.image.load(IMAGES_PATH / "logo32x32.png")
    pygame.display.set_icon(logo)
    pygame.display.set_caption("minimal program")
     
    # create a surface on screen 
    DISPLAY_SURF = pygame.display.set_mode((WIN_WIDTH,WIN_HEIGHT))
     
    # define a variable to control the main loop
    running = True

    clock = pygame.time.Clock()
    dt = 0

    g = GameGraph()

    game_data['graph'] = g
    game_data['particles'] = []

    tokens = 0
    font = pygame.font.SysFont("Arial", 30)

    game_state = GameState.MENU
    action_state = ActionState.RULE_1

    start_game_button = Button('Start', 50, 300, 100, 50)
    rule_3_button = Button('Rule 3', 500, 400, 100, 50)
    reset_button = Button('Reset', 500, 500, 100, 50)

    # main loop
    while running:
        DISPLAY_SURF.fill(pygame.color.Color("white"))
        events = pygame.event.get()

        if game_state == GameState.MENU:
            title_text = font.render('Zero Forcing Game', True, 'black')
            DISPLAY_SURF.blit(title_text, (200, 100))
            start_game_button.update()
            start_game_button.draw(DISPLAY_SURF)
            for event in events:
                if event.type == pygame.MOUSEBUTTONUP:
                    if start_game_button.hovered:
                        game_state = GameState.CHOOSE_FILE
                        start_game_button.click()

        if game_state == GameState.CHOOSE_FILE:
            # Open file selection dialog to choose file containing graph
            tkinter.Tk().withdraw()
            filename = askopenfilename(initialdir=GRAPHS_PATH)
            g = GameGraph()
            g.load_from_file(filename)
            g.game_data = game_data
            game_state = GameState.GAME

        elif game_state == GameState.GAME:
            # This is the game state representing the game being played
            # Action state tells us what action is being taken - rule 1, rule 2, etc.
            if action_state == ActionState.RULE_1:
                for event in events:
                    # Detect clicks
                    if event.type == pygame.MOUSEBUTTONUP:
                        for vertex in g.nodes:
                            if vertex.hovered and not vertex.is_filled:
                                tokens += 1
                                vertex.turn_blue()
                        if rule_3_button.hovered:
                            action_state = ActionState.RULE_3_BLUE
                            rule_3_button.click()
                        if reset_button.hovered:
                            reset_button.click()
                            for vertex in g.nodes:
                                vertex.is_filled = False
                                tokens = 0
            elif action_state == ActionState.RULE_3_BLUE:
                for event in events:
                    if event.type == pygame.MOUSEBUTTONUP:
                        if rule_3_button.hovered:
                            action_state = ActionState.RULE_1
                            rule_3_button.click()

            # Update and draw particles, edges, vertices, and buttons
            for particle in game_data['particles']:
                particle.update_pos(dt)
                particle.draw(DISPLAY_SURF)
                if not particle.is_alive:
                    game_data['particles'].remove(particle)
            for edge in g.edge_objects:
                edge.update(dt)
                edge.draw(DISPLAY_SURF)
            for vertex in g.nodes:
                vertex.update(dt)
                vertex.draw(DISPLAY_SURF)

            rule_3_button.update()
            rule_3_button.draw(DISPLAY_SURF)
            reset_button.update()
            reset_button.draw(DISPLAY_SURF)

            g.update(dt)

            tokens_surface = font.render('Tokens: '+str(tokens), True, (0,0,0))
            DISPLAY_SURF.blit(tokens_surface, (20, 20))

            if all([vertex.is_filled for vertex in g.nodes]):
                win_text_surface = font.render('All done! You used '+str(tokens)+' tokens.', True, (0,0,0))
                DISPLAY_SURF.blit(win_text_surface, (50, WIN_HEIGHT-100))

        # Regardless of game state, check for quit
        for event in events:
            if event.type == pygame.QUIT:
                running = False

        pygame.display.update()
        dt = clock.tick(60)

     
# run the main function only if this module is executed as the main script
# (if you import this as a module then nothing is executed)
if __name__=="__main__":
    # call the main function
    main()