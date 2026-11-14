import pygame
import pygwidgets
import game_essential as game

class UIGroup:
	def __init__(self, ui_dict: dict[str, ScalableButton | ScalableDisplay | FadeDisplay ]):
		self.ui_dict = ui_dict

	def add(self, key: str, ui: ScalableButton | ScalableDisplay | FadeDisplay):
		self.ui_dict[key] = ui

	def add_dict(self, ui_dict: dict[str, ScalableButton | ScalableDisplay | FadeDisplay]):
		self.ui_dict.update(ui_dict)
	
	def update(self, mouse_pos: tuple[int, int], events: list[pygame.Event]) -> dict[str, bool]:
		clicked: dict[str, bool] = {}
		for key, ui in self.ui_dict.items():
			if isinstance(ui, FadeDisplay):
				ui.trigger()
			if not isinstance(ui, ScalableButton):
				continue
			clicked[key] = ui.update(mouse_pos, events)
		
		return clicked

	def draw(self):
		for ui in self.ui_dict.values():
			ui.draw()

class PygwidgetsUIGroup:
	def __init__(self, ui_dict: dict[str, pygwidgets.TextButton]):
		self.ui_dict = ui_dict

	def add(self, key: str, ui: pygwidgets.TextButton):
		self.ui_dict[key] = ui

	def add_dict(self, ui_dict: dict[str, pygwidgets.TextButton]):
		self.ui_dict.update(ui_dict)

	def update(self, events: list[pygame.Event]) -> dict[str, bool]:
		clicked = {key: False for key in self.ui_dict.keys()}
		for key, ui in self.ui_dict.items():
			for event in events:		
				clicked[key] = True if ui.handleEvent(event) else clicked[key]
		return clicked

	def draw(self):
		for ui in self.ui_dict.values():
			ui.draw()

class ScalableButton:
	def __init__(self, screen: pygame.Surface, pos: tuple[int, int], btn_surf: pygame.Surface, btn_pressed_surf: pygame.Surface, scale: float = 1.0, anchor: str = "center", flip_x: bool = False, flip_y: bool = False):
		self.screen = screen
		btn_surf = pygame.transform.flip(btn_surf, flip_x, flip_y)
		btn_pressed_surf = pygame.transform.flip(btn_pressed_surf, flip_x, flip_y)
		self.up = btn_surf
		self.over = btn_pressed_surf
		self.pos = pos
		
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

class ScalableDisplay:
	def __init__(self, screen: pygame.Surface, pos: tuple[int, int] | pygame.Rect, surf: pygame.Surface, scale: float | int | tuple[float | int, float | int] , anchor: str = "center", flip_x: bool = False, flip_y: bool = False):
		self.screen = screen
		self.surf = pygame.transform.flip(surf, flip_x, flip_y)
		self.surf = game.scale_surface(self.surf, scale)
		self.pos = pos

		self.rect =  self.surf.get_rect()
		setattr(self.rect, anchor, pos)
        
	def draw(self):
		self.screen.blit(self.surf, (self.rect.x, self.rect.y))

class FadeDisplay:
	def __init__(self, screen: pygame.Surface, pos: tuple[int, int], surf: pygame.Surface, time_display: int, fade_start: int, fade_step: int, scale: float | int | tuple[float | int, float | int], anchor: str = "center"):
		self.screen = screen
		self.surf = game.scale_surface(surf, scale)
		self.pos = pos
		self.fade_start = fade_start
		self.fade_step = fade_step
		self.current_alpha = self.fade_start
		self.activated = False
		self.last_update = 0
		
		self.time_display = time_display
		
		self.rect = self.surf.get_rect()
		setattr(self.rect, anchor, pos)

	def trigger(self):
		self.current_alpha = self.fade_start
		self.last_update = pygame.time.get_ticks()
		self.activated = True

	def draw(self):
		if not self.activated:
			return
		
		current_time = pygame.time.get_ticks() - self.last_update
		
		if current_time >= self.time_display:
			self.current_alpha += self.fade_step
			self.surf.set_alpha(self.current_alpha)
			self.screen.blit(self.surf, (self.rect.x, self.rect.y))
			
			if self.current_alpha < 10:
				self.activated = False					
		else:
			self.surf.set_alpha(self.fade_start)
			self.screen.blit(self.surf, (self.rect.x, self.rect.y))

class Bar:
	def __init__(self, screen: pygame.Surface, base: pygame.Surface, over: pygame.Surface, border: pygame.Surface, icon: pygame.Surface, pos: tuple[int,int], scale: float | int | tuple[float | int, float | int], icon_scale: float | int | tuple[float | int, float | int]):
		self.screen = screen
		self.bar_pos = pos
		self.scale = scale

		self.base = game.scale_surface(base, scale)
		self.border = game.scale_surface(border, scale)
		self.over = game.scale_surface(over, scale)
		self.icon = game.scale_surface(icon, icon_scale)
		self.over_size = self.over.get_rect().size

		self.base_bar_rect = self.base.get_rect(topleft = pos)
		self.border_rect = self.border.get_rect(center = self.base_bar_rect.center)
		self.icon_rect = self.icon.get_rect(bottomright = self.border_rect.bottomleft)

	def draw(self, player_stats: game.PlayerStats, ratio: float | int, info: pygame.Surface):
		info_rect = info.get_rect(center = self.base_bar_rect.center)
		
		if player_stats.game_over:
			pass
		
		self.screen.blit(self.base, self.base_bar_rect)
		self.current_over = pygame.transform.scale(self.over, (self.over_size[0] * ratio, self.over_size[1]))
		self.screen.blit(self.current_over, self.bar_pos)
		self.screen.blit(self.border, self.border_rect)
		self.screen.blit(self.icon, self.icon_rect)
		self.screen.blit(info, info_rect)
		
if __name__ == "__main__":
	raise RuntimeError("This file cannot be execute directly. This file only work when imported.")