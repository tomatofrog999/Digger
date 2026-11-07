import pygame
import pygwidgets

class UIGroup:
	def __init__(self, ui_list: list[Button]):
		self.ui_list = ui_list

	def add(self, ui: Button):
		self.ui_list.append(ui)

	def add_list(self, ui_list: list[Button]):
		self.ui_list += ui_list

	def update(self, mouse_pos: tuple[int, int], events: list[pygame.Event]):
		for ui in self.ui_list:
			ui.update(mouse_pos, events)

	def draw(self):
		for ui in self.ui_list:
			ui.draw()

class Button:
	def __init__(self, screen: pygame.Surface, pos: tuple[int, int], btn_surf: pygame.Surface, btn_pressed_surf: pygame.Surface, scale: float = 1.0, anchor: str = "center", flip_x: bool = False, flip_y: bool = False):
		self.screen = screen
		btn_surf = pygame.transform.flip(btn_surf, flip_x, flip_y)
		btn_pressed_surf = pygame.transform.flip(btn_pressed_surf, flip_x, flip_y)
		self.up = btn_surf
		self.over = btn_pressed_surf
		self.pos = pos
		
		width = self.up.get_width()
		height = self.up.get_height()
		self.up = pygame.transform.scale(self.up, ((width * scale), (height * scale)))
		self.over = pygame.transform.scale(self.over, ((width * scale), (height * scale)))
		self.rect =  self.up.get_rect()
		setattr(self.rect, anchor, pos)
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