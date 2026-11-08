import pygame
import pygwidgets
import game_essential as game

class UIGroup:
	def __init__(self, ui_list: list[ScalableButton]):
		self.ui_list = ui_list

	def add(self, ui: ScalableButton):
		self.ui_list.append(ui)

	def add_list(self, ui_list: list[ScalableButton]):
		self.ui_list += ui_list

	def update(self, mouse_pos: tuple[int, int], events: list[pygame.Event]) -> list[bool]:
		clicked: list[bool] = []
		for ui in self.ui_list:
			clicked.append(ui.update(mouse_pos, events))
		
		return clicked

	def draw(self):
		for ui in self.ui_list:
			ui.draw()

class PygwidgetsUIGroup:
	def __init__(self, ui_list: list[pygwidgets.TextButton]):
		self.ui_list = ui_list

	def add(self, ui: pygwidgets.TextButton):
		self.ui_list.append(ui)

	def add_list(self, ui_list: list[pygwidgets.TextButton]):
		self.ui_list += ui_list

	def update(self, events: list[pygame.Event]) -> list[bool]:
		clicked = [False for _ in range(len(self.ui_list))]
		for i in range(len(self.ui_list)):
			ui = self.ui_list[i]
			for event in events:		
				clicked[i] = True if ui.handleEvent(event) else clicked[i]
		return clicked

	def draw(self):
		for ui in self.ui_list:
			ui.draw()

class ScalableButton:
	def __init__(self, screen: pygame.Surface, pos: tuple[int, int], btn_surf: pygame.Surface, btn_pressed_surf: pygame.Surface, scale: float = 1.0, anchor: str = "center", flip_x: bool = False, flip_y: bool = False):
		self.screen = screen
		btn_surf = pygame.transform.flip(btn_surf, flip_x, flip_y)
		btn_pressed_surf = pygame.transform.flip(btn_pressed_surf, flip_x, flip_y)
		self.up = btn_surf
		self.over = btn_pressed_surf
		self.pos = pos
		
		width = self.up.get_width()
		height = self.up.get_height()
		self.up = game.scale_surface(self.up, scale)
		self.over = game.scale_surface(self.over, scale)
		self.rect =  self.up.get_rect()
		setattr(self.rect, anchor, pos)
		self.activated = False
		self.clicked = False

	def update(self, mouse_pos: tuple[int, int], events: list[pygame.Event]) -> bool:
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

		return self.clicked
        
	def draw(self):
		if self.activated:
			self.screen.blit(self.over, (self.rect.x, self.rect.y))
		else:
			self.screen.blit(self.up, (self.rect.x, self.rect.y))

if __name__ == "__main__":
	raise RuntimeError("This file cannot be execute directly. This file only work when imported.")