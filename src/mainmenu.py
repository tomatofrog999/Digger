import pygame
import game_essential as game
import os
import sys
import main

CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
BASE_PATH = os.path.dirname(CURRENT_PATH)
ASSET_PATH = os.path.join(BASE_PATH, "assets")
IMAGE_PATH = os.path.join(ASSET_PATH, "images")

pygame.init()

FULLSCREEN = True
screen_info = pygame.display.Info()
ORIGINAL_SCREEN_WIDTH = 800
ORIGINAL_SCREEN_HEIGHT = 600
SCREEN_WIDTH = screen_info.current_w if FULLSCREEN else ORIGINAL_SCREEN_WIDTH
SCREEN_HEIGHT = screen_info.current_h if FULLSCREEN else ORIGINAL_SCREEN_HEIGHT
FPS = 20
PLAY_X = round(SCREEN_WIDTH / 2)
PLAY_Y = round(SCREEN_HEIGHT / 1.55)
EXIT_Y = round(SCREEN_HEIGHT / 1.325)
BUTTON_SCALE = 4

class Button:
	def __init__(self, screen: pygame.Surface ,pos: tuple[int, int], up: pygame.Surface, over: pygame.Surface, scale: int):
		self.screen = screen
		self.up = up
		self.over = over
		width = self.up.get_width()
		height = self.up.get_height()
		self.up = pygame.transform.scale(self.up, ((width * scale), (height * scale)))
		self.over = pygame.transform.scale(self.over, ((width * scale), (height * scale)))
		self.rect =  self.up.get_rect()
		self.rect.center = pos
		self.activated = False
		self.clicked = False

	def update(self, mouse_position: tuple[int, int], pressed_right_click: bool):
		if self.rect.collidepoint(mouse_position):
			self.activated = True
			if pressed_right_click:
				self.clicked = True
		else:
			self.activated = False
			self.clicked = False
        
	def draw(self):
		if self.activated:
			self.screen.blit(self.over, (self.rect.x, self.rect.y))
		else:
			self.screen.blit(self.up, (self.rect.x, self.rect.y))


def main_menu():
	screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
	clock = pygame.time.Clock()
    
	play_up_surf = game.load_picture(os.path.join(IMAGE_PATH, "play.png"), True)
	play_over_surf = game.load_picture(os.path.join(IMAGE_PATH, 'play_over.png'), True)
	exit_up_surf = game.load_picture(os.path.join(IMAGE_PATH, "exit.png"), True)
	exit_over_surf = game.load_picture(os.path.join(IMAGE_PATH, "exit_over.png"), True)
        
	play_button = Button(screen, (round(PLAY_X), round(PLAY_Y)), play_up_surf, play_over_surf, BUTTON_SCALE)
	exit_button = Button(screen, (round(PLAY_X), round(EXIT_Y)), exit_up_surf, exit_over_surf, BUTTON_SCALE)
	running = True
    
	while running:
		events = pygame.event.get()
		for event in events:
			if event.type == pygame.QUIT:
				running = False
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					running = False
                    
		mouse_pos = pygame.mouse.get_pos()
		mouse_key = pygame.mouse.get_pressed()

		play_button.update(mouse_pos, mouse_key[0])
		exit_button.update(mouse_pos, mouse_key[0])

		if exit_button.clicked:
			running = False

		if play_button.clicked:
			main.main()
        
		screen.fill('black')
		play_button.draw()
		exit_button.draw()
		pygame.display.flip()

		clock.tick(FPS)

	pygame.quit()
	sys.exit()

main_menu()