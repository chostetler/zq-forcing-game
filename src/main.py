# import the pygame module, so you can use it
from argparse import Action
import pygame
import math
import tkinter
from tkinter.filedialog import askopenfilename
from enum import Enum, auto
from config import *
import entities.graphcomponents as gc
from state.states import GameState, ActionState
 
class Button():
    def __init__(self, text, x, y, width, height, visible=True, font=None, hover_color=(150, 150, 255), enabled=True, visible_states=[s.value for s in ActionState]):
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
        self.visible = visible
        self.enabled = enabled
        self.surface = pygame.Surface(self.rect.size)

    def update(self, dt=60):
        self.hovered = self.rect.collidepoint(pygame.mouse.get_pos())
        self.draw_color = self.hover_color if self.hovered else 'white'

    def render(self, surface: pygame.surface.Surface):
        if self.visible:
            pygame.draw.rect(surface, self.draw_color, self.rect)
            pygame.draw.rect(surface, 'black', self.rect, 4)
            button_text = self.font.render(self.text, True, 'black')
            surface.blit(button_text, (self.x+5, self.y+5))

    def click(self):
        click_sound = pygame.mixer.Sound(SOUNDS_PATH / 'menu-bip.wav')
        click_sound.play()

class ForceArrow:
    def __init__(self, origin: 'gc.Vertex', destination: 'gc.Vertex'):
        self.origin = origin
        self.destination = destination

    def render(self, surface: pygame.surface.Surface):
        self.origin_coords = (self.origin.x, self.origin.y)
        self.destination_coords = (self.destination.x, self.destination.y)
        self.center_coords = (self.origin_coords + self.destination_coords) / 2
        self.dy, self.dx = (self.destination_coords - self.origin_coords)

        self.angle = math.atan2(self.dy, self.dx)
        arrow_image = pygame.image.load(IMAGES_PATH / 'force-arrow.png')
        arrow_rotated = pygame.transform.rotate(arrow_image, self.angle)

        arrow_rotated.blit(surface, arrow_rotated.get_rect(center=self.center_coords))

class Game:
    def __init__(self) -> None:
        pygame.init()
        # load and set the logo
        logo = pygame.image.load(IMAGES_PATH / "logo32x32.png")
        pygame.display.set_icon(logo)
        pygame.display.set_caption("Zq forcing game")
        
        # create a surface on screen 
        self.DISPLAY_SURF = pygame.display.set_mode((WIN_WIDTH,WIN_HEIGHT))
        
        # define a variable to control the main loop
        self.running = True

        self.clock = pygame.time.Clock()
        self.dt = 0

        self.game_state = GameState.MENU
        self.action_state = ActionState.RULE_1

        self.g = gc.GameGraph(parent_game=self)
        self.particles = []
        self.tokens = 0
        self.font = pygame.font.SysFont("Arial", 30)

        self.token_vertices = []

        self.start_game_button = Button('Start', 50, 300, 100, 50)
        self.reset_button = Button('Reset', 500, 550, 100, 50, visible_states=[ActionState.RULE_1, ActionState.RULE_3_BLUE, ActionState.RULE_3_FORCE])
        self.rule_3_button = Button('Rule 3', 500, 480, 100, 50)
        self.rule_3_cancel_button = Button('Cancel', 50, 500, 100, 50)
        self.rule_3_blue_confirm_button = Button('Confirm', 160, 500, 100, 50)
        self.rule_3_white_confirm_button = Button('Confirm', 160, 500, 100, 50)
        self.rule_3_done_button = Button('Done', 50, 500, 100, 50)
        self.buttons = [self.start_game_button, self.reset_button, self.rule_3_button, self.rule_3_cancel_button, self.rule_3_blue_confirm_button, self.rule_3_white_confirm_button, self.rule_3_done_button]

        self.sounds = {}
        self.sounds['menu-bip'] = pygame.mixer.Sound(SOUNDS_PATH / 'menu-bip.wav')
        self.sounds['menu-bip-low'] = pygame.mixer.Sound(SOUNDS_PATH / 'menu-bip-low.wav')
        self.sounds['whoosh'] = pygame.mixer.Sound(SOUNDS_PATH / 'whoosh.wav')
        self.sounds['bwang'] = pygame.mixer.Sound(SOUNDS_PATH / 'bwang.wav')

    def game_loop(self) -> None:
        self.handle_events()
        self.update()
        self.render()
        self.clock_tick()

    def handle_events(self):
        '''Handle events provided by pygame'''
        self.events = pygame.event.get()
        self.clicked_object = None
        self.clicked_objects = []

        if self.game_state == GameState.MENU:
            title_text = self.font.render('Zero Forcing Game', True, 'black')
            self.DISPLAY_SURF.blit(title_text, (200, 100))
            self.start_game_button.update()
            self.start_game_button.render(self.DISPLAY_SURF)
            for event in self.events:
                if event.type == pygame.MOUSEBUTTONUP:
                    if self.start_game_button.hovered:
                        self.game_state = GameState.CHOOSE_FILE
                        self.start_game_button.click()

        elif self.game_state == GameState.CHOOSE_FILE:
            # Open file selection dialog to choose file containing graph
            tkinter.Tk().withdraw()
            filename = askopenfilename(initialdir=GRAPHS_PATH)
            self.g = gc.GameGraph(parent_game=self)
            self.g.load_from_file(filename)
            self.game_state = GameState.GAME
            
            self.blue_first_selection = gc.Selection(self.g)
            self.white_selection = gc.Selection(self.g)

        elif self.game_state == GameState.GAME:
            # This is the game state representing the game being played
            # Action state tells us what action is being taken - rule 1, rule 2, etc.
            for event in self.events:
                if event.type == pygame.MOUSEBUTTONUP:
                    # Figure out what object got clicked
                    for edge in self.g.edge_objects:
                        if edge.hovered and edge.visible and edge.is_forceable: self.clicked_objects.append(edge)
                    for vertex in self.g.nodes:
                        if vertex.hovered and vertex.visible: self.clicked_objects.append(vertex)
                    for button in self.buttons:
                        if button.hovered and button.visible: self.clicked_objects.append(button)
                    
                    if len(self.clicked_objects) >= 1:
                        self.clicked_object = self.clicked_objects[-1]
        
        for event in self.events:
            if event.type == pygame.QUIT:
                self.running = False

    def update(self) -> None:
        '''Update game data'''
        # First - deal with clicks
        if self.action_state == ActionState.RULE_1:
            if self.clicked_object in self.g.nodes:
                vertex = self.clicked_object
                if not vertex.is_filled:
                    self.tokens += 1
                    vertex.turn_blue()
                    self.token_vertices.append(vertex)
                    self.g.update_connected_components()
            if self.clicked_object in self.g.edge_objects:
                edge: gc.Edge = self.clicked_object
                if edge.is_forceable:
                    edge.origin.turn_blue()
                    edge.destination.turn_blue()
                    self.g.update_connected_components()
            if self.clicked_object is self.rule_3_button:
                self.action_state = ActionState.RULE_3_BLUE
                self.rule_3_button.click()

        elif self.action_state == ActionState.RULE_3_BLUE:
            if self.clicked_object in self.g.nodes:
                vertex = self.clicked_object
                if not vertex.is_filled:
                    component = self.g.connected_component(vertex)
                    if component in self.g.blue_selection.components:
                        self.g.blue_selection.components.remove(component)
                        self.sounds['menu-bip-low'].play()
                    else:
                        self.g.blue_selection.components.append(component)
                        self.sounds['menu-bip'].play()
            if self.clicked_object is self.rule_3_cancel_button:
                self.rule_3_cancel_button.click()
                self.action_state = ActionState.RULE_1
            if self.clicked_object is self.rule_3_blue_confirm_button:
                if len(self.g.blue_selection.components) > Q:
                    self.action_state = ActionState.RULE_3_WHITE
                    self.sounds['whoosh'].play()
                else:
                    self.sounds['bwang'].play()

        elif self.action_state == ActionState.RULE_3_WHITE:
            if self.clicked_object in self.g.nodes:
                vertex: gc.Vertex = self.clicked_object
                if not vertex.is_filled:
                    component = self.g.connected_component(vertex)
                    if component in self.g.white_selection.components:
                        self.g.white_selection.components.remove(component)
                        self.sounds['menu-bip-low'].play()
                    else:
                        self.g.white_selection.components.append(component)
                        self.sounds['menu-bip'].play()
            if self.clicked_object is self.rule_3_white_confirm_button:
                if len(self.g.white_selection.components) >= 1:
                    self.action_state = ActionState.RULE_3_FORCE
                    self.sounds['whoosh'].play()
                else:
                    self.sounds['bwang'].play()

        elif self.action_state == ActionState.RULE_3_FORCE:
            if self.clicked_object in self.g.edge_objects:
                edge: gc.Edge = self.clicked_object
                if edge.is_forceable:
                    edge.origin.turn_blue()
                    edge.destination.turn_blue()
            if self.clicked_object is self.rule_3_done_button:
                self.action_state = ActionState.RULE_1
                self.g.update_connected_components()


        if self.clicked_object is self.reset_button:
            self.reset_button.click()
            self.token_vertices = []
            self.action_state = ActionState.RULE_1
            for vertex in self.g.nodes:
                vertex.is_filled = False
                vertex.has_forced = False
                self.tokens = 0
            self.g.update_connected_components()

        # Update positions of objects
        for particle in self.particles:
            particle.update_pos(self.dt)
            if not particle.is_alive:
                self.particles.remove(particle)
        for edge in self.g.edge_objects:
            edge.update(self.dt)
        for vertex in self.g.nodes:
            vertex.update(self.dt)
        for button in self.buttons:
            button.update()
        self.g.update(self.dt)

    def render(self) -> None:
        '''Display things based on our game data'''
        self.DISPLAY_SURF.fill(pygame.color.Color("white"))
        self.hide_all_buttons()

        if self.game_state == GameState.MENU:
            self.start_game_button.visible = True
            self.start_game_button.visible = True
            self.title_text = self.font.render('Zero Forcing Game', True, 'black')
            self.DISPLAY_SURF.blit(self.title_text, (200, 100))
            self.start_game_button.render(self.DISPLAY_SURF)

        elif self.game_state == GameState.GAME:
            for particle in self.particles:
                particle.render(self.DISPLAY_SURF)
            for edge in self.g.edge_objects:
                edge.render(self.DISPLAY_SURF)
            for vertex in self.g.nodes:
                vertex.render(self.DISPLAY_SURF)

            self.reset_button.visible = True
            if self.action_state == ActionState.RULE_1:
                self.rule_3_button.visible = True
                for vertex in self.g.nodes:
                    if vertex.hovered and not vertex.is_filled:
                        token_image = pygame.transform.scale(pygame.image.load(IMAGES_PATH / 'token.png'), (15, 15))
                        token_pos = (pygame.mouse.get_pos()[0]+10, pygame.mouse.get_pos()[1]-5)
                        self.DISPLAY_SURF.blit(token_image, token_image.get_rect(center=token_pos))

            elif self.action_state == ActionState.RULE_3_BLUE:
                if SHOW_RULE_3_INSTRUCTIONS: self.DISPLAY_SURF.blit(self.font.render('1. BLUE: select at least q+1 components (q='+str(Q)+')', True, RULE_3_HOVER_COLOR), (200, 0))
                self.rule_3_blue_confirm_button.visible = True
                self.rule_3_cancel_button.visible = True
                self.reset_button.visible = False
            elif self.action_state == ActionState.RULE_3_WHITE:
                if SHOW_RULE_3_INSTRUCTIONS: self.DISPLAY_SURF.blit(self.font.render('2. WHITE: select at least 1 component', True, RULE_3_HOVER_COLOR), (200, 0))
                self.rule_3_white_confirm_button.visible = True
                self.reset_button.visible = False
            elif self.action_state == ActionState.RULE_3_FORCE:
                if SHOW_RULE_3_INSTRUCTIONS: self.DISPLAY_SURF.blit(self.font.render('3. BLUE: perform color forcing (if possible)', True, FILLED_COLOR), (200, 0))
                self.rule_3_done_button.visible = True
                self.reset_button.visible = False

            for button in self.buttons:
                button.render(self.DISPLAY_SURF)

            self.tokens_surface = self.font.render('Tokens: '+str(self.tokens), True, (0,0,0))
            self.DISPLAY_SURF.blit(self.tokens_surface, (20, 20))

            if all([vertex.is_filled for vertex in self.g.nodes]):
                win_text_surface = self.font.render('All done! Blue used '+str(self.tokens)+' tokens.', True, (0,0,0))
                self.DISPLAY_SURF.blit(win_text_surface, (50, WIN_HEIGHT-100))

        pygame.display.update()

    def clock_tick(self) -> None:
        '''Tick the clock for pygame, updating self.dt'''
        self.dt = self.clock.tick(60)

    def hide_all_buttons(self):
        for button in self.buttons:
            button.visible = False



#############################################################
  
# run the main function only if this module is executed as the main script
# (if you import this as a module then nothing is executed)
if __name__=="__main__":
    # call the main function
    game = Game()
    while game.running:
        game.game_loop()