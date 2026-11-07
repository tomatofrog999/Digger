import pygame
import game_essential as game

class UIGroup:
	def __init__(self, ui_list: list[ScalableButton]):
		self.ui_list = ui_list

	def add(self, ui: ScalableButton):
		self.ui_list.append(ui)

	def add_list(self, ui_list: list[ScalableButton]):
		self.ui_list += ui_list

	def update(self, mouse_pos: tuple[int, int], events: list[pygame.Event]):
		for ui in self.ui_list:
			ui.update(mouse_pos, events)

	def draw(self):
		for ui in self.ui_list:
			ui.draw()

class ScalableButton:
	def __init__(self, screen: pygame.Surface ,pos: tuple[int, int], btn_surf: pygame.Surface, btn_pressed_surf: pygame.Surface, scale: int):
		self.screen = screen
		self.up = btn_surf
		self.over = btn_pressed_surf
		width = self.up.get_width()
		height = self.up.get_height()
		self.up = game.scale_surface(self.up, scale)
		self.over = game.scale_surface(self.over, scale)
		self.rect =  self.up.get_rect()
		self.rect.center = pos
		self.activated = False
		self.clicked = False

	def update(self, mouse_pos: tuple[int, int], events: list[pygame.Event]):
		right_click_up = False
		for event in events:
			if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
				right_click_up = True

		if self.clicked:
			self.clicked = False

		if self.rect.collidepoint(mouse_pos):
			self.activated = True
			if right_click_up and not self.clicked:
				self.clicked = True
		else:
			self.activated = False
        
	def draw(self):
		if self.activated:
			self.screen.blit(self.over, (self.rect.x, self.rect.y))
		else:
			self.screen.blit(self.up, (self.rect.x, self.rect.y))

if __name__ == "__main__":
	raise RuntimeError("This file cannot be execute directly. This file only work when imported.")