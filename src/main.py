import pygame
import sys
import os
import game_essential as game
import game_ui as ui
import pygwidgets
from game_constant import *
import math

def main():
	screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
	pygame.display.set_caption("Digger Game")
	pygame.font.init()

	player_stats = game.PlayerStats().init_break_damage(START_BREAK_DAMAGE, START_BREAK_DAMAGE_MODIFIER).init_max_block(START_MAX_INVENTORY) \
				.init_max_energy(START_ENERGY).init_max_health(START_HEALTH).init_on_beat_constant(START_ON_BEAT_EXTRA_DMG, START_ON_BEAT_EXTRA_DMG_MODIFIER) \
				.init_convertion_ratio(START_CONVERTION_RATIO)
	player_stats.check_init()

	scene_manager = SceneManager(MAIN_MENU_SCENE_KEY)
	main_menu_scene = MainMenuScene(screen, scene_manager)
	main_scene = MainScene(screen, scene_manager, player_stats)
	pause_scene = PauseScene(screen, scene_manager)
	shop_scene = ShopScene(screen, scene_manager, player_stats)
	bar_scene = BarScene(screen, scene_manager, player_stats)
	game_over_scene = GameOverScene(screen, scene_manager, player_stats)
	scene_manager.scenes[MAIN_MENU_SCENE_KEY] = main_menu_scene
	scene_manager.scenes[MAIN_SCENE_KEY] = main_scene
	scene_manager.scenes[PAUSE_SCENE_KEY] = pause_scene
	scene_manager.scenes[SHOP_SCENE_KEY] = shop_scene
	scene_manager.scenes[BAR_SCENE_KEY] = bar_scene
	scene_manager.scenes[GAME_OVER_KEY] = game_over_scene
	scene_manager.start()

	while scene_manager.running:
		scene_manager.run_loop()

	print("\n\n")
	pygame.quit()
	sys.exit()

class Scene:
	def __init__(self, screen: pygame.Surface, scene_manager: SceneManager):
		self.screen = screen
		self.scene_manager = scene_manager
		self.started = False
		self.running = False
		self.is_pause = False
		self.can_pause = False
		self.dt = 0
		self.clock = pygame.time.Clock()

	def start(self):
		if not self.started:
			self.started = True

	def run_loop(self):
		if not self.started:
			self.start()

	def stop(self):
		self.started = False

	def pause(self):
		if not self.started:
			self.start()
		self.is_pause = True

	def unpause(self):
		if not self.started:
			self.start()
		self.is_pause = False

class SceneManager:
	def __init__(self, start_scene_key: str, scenes: dict[str, Scene] = {}):
		self.scenes = scenes
		self.scene_key = start_scene_key
		self.scenes_key_stack = []
		self.running = False

	def start(self):
		self.running = True
		current_scene = self.scenes[self.scene_key]
		current_scene.start()

	def stop(self):
		self.reset_stack()
		current_scene = self.scenes[self.scene_key]
		current_scene.stop()
		self.running = False

	def change_scene(self, new_scene_key: str, reset_stack: bool = False):
		if new_scene_key not in self.scenes:
			raise ValueError("Incorrect scene key.")
		
		current_scene = self.scenes[self.scene_key]

		if current_scene.can_pause and not reset_stack:
			current_scene.pause()
		else:
			current_scene.stop()
		self.scenes_key_stack.append(self.scene_key)

		if reset_stack:
			self.reset_stack()
		
		self.scene_key = new_scene_key
		current_scene = self.scenes[self.scene_key]
		current_scene.start()

	def reset_stack(self):
		for key in self.scenes_key_stack:
			if key not in self.scenes:
				self.scenes_key_stack.remove(key)
				continue
			self.scenes[key].stop()
		self.scenes_key_stack = []

	def go_back(self):
		if len(self.scenes_key_stack) == 0:
			return
		current_scene = self.scenes[self.scene_key]
		current_scene.stop()

		old_scene_key = self.scenes_key_stack.pop()
		old_scene = self.scenes[old_scene_key]
		if old_scene.can_pause:
			old_scene.unpause()
		else:
			old_scene.start()
		self.scene_key = old_scene_key

	def run_loop(self):
		current_scene = self.scenes[self.scene_key]
		current_scene.run_loop()


class MainMenuScene(Scene):
	PLAY_BUTTON = "play"
	EXIT_BUTTON = "exit"
	LOGO_DISPLAY = "logo"
	NEW_GAME_BUTTON = "new_game"

	def __init__(self, screen: pygame.Surface, scene_manager: SceneManager):
		super().__init__(screen, scene_manager)

		NEW_GAME_Y = round(SCREEN_HEIGHT / 1.75)
		PLAY_BTN_Y = round(SCREEN_HEIGHT / 1.45)
		EXIT_BTN_Y = round(SCREEN_HEIGHT / 1.225)
		LOGO_Y = round(SCREEN_HEIGHT / 2.85)
		BUTTON_SCALE = SCREEN_WIDTH / SCREEN_HEIGHT * 4 if FULL_SCREEN else 4
		LOGO_SCALE = SCREEN_WIDTH / SCREEN_HEIGHT * 2 if FULL_SCREEN else 2

		# Main Menu
		play_up_surf = game.load_picture(os.path.join(IMAGE_UI_PATH, "continue.png"), True)
		play_over_surf = game.load_picture(os.path.join(IMAGE_UI_PATH, 'continue_over.png'), True)
		exit_up_surf = game.load_picture(os.path.join(IMAGE_UI_PATH, "exit_to_desktop.png"), True)
		exit_over_surf = game.load_picture(os.path.join(IMAGE_UI_PATH, "exit_to_desktop_over.png"), True)
		logo_surf = game.load_picture(os.path.join(IMAGE_UI_PATH, "logo.png"), True)
		new_game_surf = game.load_picture(os.path.join(IMAGE_UI_PATH, "new_game.png"), True)
		new_game_over_surf = game.load_picture(os.path.join(IMAGE_UI_PATH, "new_game_over.png"), True)
		
		# Main Menu Button
		new_game_button = ui.ScalableButton(screen, (SCREEN_WIDTH_HALF, NEW_GAME_Y), new_game_surf, new_game_over_surf, BUTTON_SCALE)
		play_button = ui.ScalableButton(screen, (SCREEN_WIDTH_HALF, PLAY_BTN_Y), play_up_surf, play_over_surf, BUTTON_SCALE)
		exit_button = ui.ScalableButton(screen, (SCREEN_WIDTH_HALF, EXIT_BTN_Y), exit_up_surf, exit_over_surf, BUTTON_SCALE)
		logo = ui.ScalableDisplay(screen, (SCREEN_WIDTH_HALF, LOGO_Y), logo_surf, LOGO_SCALE)
	
		self.main_menu_group = ui.UIGroup({ 
			MainMenuScene.PLAY_BUTTON: play_button, 
			MainMenuScene.EXIT_BUTTON: exit_button,
			MainMenuScene.LOGO_DISPLAY: logo,
			MainMenuScene.NEW_GAME_BUTTON: new_game_button
		})

	def run_loop(self):
		super().run_loop()
		events = pygame.event.get()
		for event in events:
			if event.type == pygame.QUIT:
				self.scene_manager.stop()
				return
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					self.scene_manager.stop()
					return

		self.screen.fill("#171722")

		mouse_pos = pygame.mouse.get_pos()
		clicked = self.main_menu_group.update(mouse_pos, events)

		if clicked[MainMenuScene.PLAY_BUTTON]:
			self.scene_manager.change_scene(MAIN_SCENE_KEY, reset_stack=True)

		if clicked[MainMenuScene.EXIT_BUTTON]:
			self.scene_manager.stop()
			return

		if clicked[MainMenuScene.NEW_GAME_BUTTON]:
			game.delete_save(AUTO_SAVE_FILE_NAME)
			self.scene_manager.change_scene(MAIN_SCENE_KEY, reset_stack=True)

		self.main_menu_group.draw()

		pygame.display.flip()

		self.dt = self.clock.tick(FPS_UI) / 1000
		self.dt = min(self.dt, 1 / FPS_UI)

class PauseScene(Scene):
	PLAY_BUTTON = "play"
	EXIT_BUTTON = "exit"
	LOGO_DISPLAY = "logo"
	EXIT_DESKTOP = "exit_desktop"

	def __init__(self, screen: pygame.Surface, scene_manager: SceneManager):
		super().__init__(screen, scene_manager)

		PLAY_BTN_Y = round(SCREEN_HEIGHT / 1.75)
		EXIT_BTN_Y = round(SCREEN_HEIGHT / 1.45)
		EXIT_DESKTOP_Y = round(SCREEN_HEIGHT / 1.225)
		LOGO_Y = round(SCREEN_HEIGHT / 2.85)
		BUTTON_SCALE = SCREEN_WIDTH / SCREEN_HEIGHT * 4 if FULL_SCREEN else 4
		LOGO_SCALE = SCREEN_WIDTH / SCREEN_HEIGHT * 2 if FULL_SCREEN else 2

		# Main Menu
		play_up_surf = game.load_picture(os.path.join(IMAGE_UI_PATH, "continue.png"), True)
		play_over_surf = game.load_picture(os.path.join(IMAGE_UI_PATH, 'continue_over.png'), True)
		exit_up_surf = game.load_picture(os.path.join(IMAGE_UI_PATH, "exit.png"), True)
		exit_over_surf = game.load_picture(os.path.join(IMAGE_UI_PATH, "exit_over.png"), True)
		logo_surf = game.load_picture(os.path.join(IMAGE_UI_PATH, "pause_logo.png"), True)
		exit_desktop_surf = game.load_picture(os.path.join(IMAGE_UI_PATH, "exit_to_desktop.png"), True)
		exit_desktop_over_surf = game.load_picture(os.path.join(IMAGE_UI_PATH, "exit_to_desktop_over.png"), True)
		
		# Main Menu Button
		play_button = ui.ScalableButton(screen, (SCREEN_WIDTH_HALF, PLAY_BTN_Y), play_up_surf, play_over_surf, BUTTON_SCALE)
		exit_button = ui.ScalableButton(screen, (SCREEN_WIDTH_HALF, EXIT_BTN_Y), exit_up_surf, exit_over_surf, BUTTON_SCALE)
		logo = ui.ScalableDisplay(screen, (SCREEN_WIDTH_HALF, LOGO_Y), logo_surf, LOGO_SCALE)
		exit_desktop_button = ui.ScalableButton(screen, (SCREEN_WIDTH_HALF, EXIT_DESKTOP_Y), exit_desktop_surf, exit_desktop_over_surf, BUTTON_SCALE)
			
		self.main_menu_group = ui.UIGroup({ 
			PauseScene.PLAY_BUTTON: play_button, 
			PauseScene.EXIT_BUTTON: exit_button,
			PauseScene.LOGO_DISPLAY: logo,
			PauseScene.EXIT_DESKTOP: exit_desktop_button
		})

	def run_loop(self):
		super().run_loop()
		events = pygame.event.get()
		for event in events:
			if event.type == pygame.QUIT:
				self.scene_manager.stop()
				return
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					self.scene_manager.go_back()
					return

		self.screen.fill("#40983C")

		mouse_pos = pygame.mouse.get_pos()
		clicked = self.main_menu_group.update(mouse_pos, events)

		if clicked[PauseScene.PLAY_BUTTON]:
			self.scene_manager.go_back()
			return

		if clicked[PauseScene.EXIT_BUTTON]:
			self.scene_manager.change_scene(MAIN_MENU_SCENE_KEY, reset_stack=True)
			return

		if clicked[PauseScene.EXIT_DESKTOP]:
			self.scene_manager.stop()
			return

		self.main_menu_group.draw()

		pygame.display.flip()

		self.dt = self.clock.tick(FPS_UI) / 1000
		self.dt = min(self.dt, 1 / FPS_UI)

class MainScene(Scene):
	def __init__(self, screen: pygame.Surface, scene_manager: SceneManager, player_stats: game.PlayerStats):
		super().__init__(screen, scene_manager)
		self.can_pause = True
		self.player_stats = player_stats

		self.break_effect_sheet = game.load_picture(os.path.join(IMAGE_MAIN_PATH, "break_effect.png"), True)
		SPRITE_SHEET_SURFACE = game.load_picture(os.path.join(IMAGE_MAIN_PATH, "tiles_spritesheet.png"), True)
		# Layer 1
		BLOCK1_SURFACE_DATA = game.get_spritesheet_data(os.path.join(IMAGE_MAIN_PATH, "tiles_spritesheet.txt"), "grassCenter")
		BLOCK1_SURFACE = game.get_surface_from_sprite_sheet2(SPRITE_SHEET_SURFACE, BLOCK1_SURFACE_DATA[0], BLOCK1_SURFACE_DATA[1], (BLOCK_WIDTH / BLOCK1_SURFACE_DATA[1][0]), False)
		BLOCK1_DATA = game.BlockData(BLOCK1_SURFACE, 3.0, 0.8)
		
		BLOCK2_SURFACE_DATA = game.get_spritesheet_data(os.path.join(IMAGE_MAIN_PATH, "tiles_spritesheet.txt"), "stoneCenter")
		BLOCK2_SURFACE = game.get_surface_from_sprite_sheet2(SPRITE_SHEET_SURFACE, BLOCK2_SURFACE_DATA[0], BLOCK2_SURFACE_DATA[1], (BLOCK_WIDTH / BLOCK2_SURFACE_DATA[1][0]), False)
		BLOCK2_DATA = game.BlockData(BLOCK2_SURFACE, 6.0, 0.2)
		
		LAYER1_DATA = game.LayerData(10, (BLOCK1_DATA, BLOCK2_DATA)).init_bomb(0.05, 1).init_energy(0.02, 20) \
					.init_treasure(0.01, 10).init_multiblock_rate(0.01).init_energy_usage(1)
		LAYER1_DATA.check_init()
		
		
		# Layer 2
		BLOCK3_SURFACE = pygame.Surface((BLOCK_WIDTH, BLOCK_HEIGHT))
		BLOCK3_SURFACE.fill("orange")
		BLOCK3_DATA = game.BlockData(BLOCK3_SURFACE, 10.0, 0.6)
		
		BLOCK4_SURFACE = pygame.Surface((BLOCK_WIDTH, BLOCK_HEIGHT))
		BLOCK4_SURFACE.fill("pink")
		BLOCK4_DATA = game.BlockData(BLOCK4_SURFACE, 15.0, 0.4)
		
		LAYER2_DATA = game.LayerData(25, (BLOCK3_DATA, BLOCK4_DATA)).init_bomb(0.06, 2).init_energy(0.03, 40) \
					.init_treasure(0.015, 30).init_multiblock_rate(0.02).init_energy_usage(2)
		LAYER2_DATA.check_init()
		
		# Layer 3
		BLOCK5_SURFACE = pygame.Surface((BLOCK_WIDTH, BLOCK_HEIGHT))
		BLOCK5_SURFACE.fill("darkorchid1")
		BLOCK5_DATA = game.BlockData(BLOCK5_SURFACE, 20.0, 0.15)
		
		BLOCK6_SURFACE = pygame.Surface((BLOCK_WIDTH, BLOCK_HEIGHT))
		BLOCK6_SURFACE.fill("darkmagenta")
		BLOCK6_DATA = game.BlockData(BLOCK6_SURFACE, 35.0, 0.8)
		
		BLOCK7_SURFACE = pygame.Surface((BLOCK_WIDTH, BLOCK_HEIGHT))
		BLOCK7_SURFACE.fill("plum2")
		BLOCK7_DATA = game.BlockData(BLOCK7_SURFACE, 40.0, 0.05)
		
		LAYER3_DATA = game.LayerData(50, (BLOCK5_DATA, BLOCK6_DATA, BLOCK7_DATA)).init_bomb(0.15, 3).init_energy(0.07, 80) \
					.init_treasure(0.05, 80).init_multiblock_rate(0.03).init_energy_usage(4)
		LAYER3_DATA.check_init()
		
		BOMB_SURFACE = pygame.Surface((BLOCK_WIDTH, BLOCK_HEIGHT))
		BOMB_SURFACE.fill("red")
		ENERGY_SURFACE = pygame.Surface((BLOCK_WIDTH, BLOCK_HEIGHT))
		ENERGY_SURFACE.fill("green")
		TREASURE_SURFACE = pygame.Surface((BLOCK_WIDTH, BLOCK_HEIGHT))
		TREASURE_SURFACE.fill("blue")
		MAP1_DATA = game.MapData((LAYER1_DATA, LAYER2_DATA, LAYER3_DATA), BLOCK_WIDTH, BLOCK_HEIGHT, BOMB_SURFACE, ENERGY_SURFACE, TREASURE_SURFACE)

		self.underground_surface = pygame.Surface((BLOCK_WIDTH * BLOCK_PER_WIDTH, BLOCK_HEIGHT * (BLOCK_PER_HEIGHT + 4)))
		self.underground_surface.fill("#2A2319")
		
		self.platform_group = pygame.sprite.Group()
		
		PLATFORM1_SURFACE = pygame.Surface((BLOCK_WIDTH * BLOCK_PER_WIDTH * 4, BLOCK_HEIGHT * (BLOCK_PER_HEIGHT + 4)))
		PLATFORM1_SURFACE.fill("#574E35")
		PLATFORM2_SURFACE = PLATFORM1_SURFACE.copy()
		
		PLATFORM1 = game.PlatformSprite(PLATFORM1_SURFACE, (0, 0))
		PLATFORM1.get_rect().topright = MINE_POS
		
		PLATFORM2 = game.PlatformSprite(PLATFORM2_SURFACE, (MINE_POS[0] + BLOCK_WIDTH * BLOCK_PER_WIDTH, MINE_POS[1]))

		PLATFORM3_SURFACE = pygame.Surface((BLOCK_WIDTH * 1, BLOCK_HEIGHT * 10))
				
		PLATFORM3 = game.PlatformSprite(PLATFORM3_SURFACE, (0, 0), invisible=True)
		PLATFORM3.get_rect().bottomright = (CAM_CUTOFF_LEFT, MINE_POS[1])

		PLATFORM4_SURFACE = PLATFORM3_SURFACE.copy()
		
		PLATFORM4 = game.PlatformSprite(PLATFORM4_SURFACE, (0, 0), invisible=True)
		PLATFORM4.get_rect().bottomleft = (CAM_CUTOFF_RIGHT, MINE_POS[1])

		self.game_state = game.GameState(MAP1_DATA, WORLD_START_SEED)
		self.game_state.create_new_block_group()
		self.platform_group.add(PLATFORM1)
		self.platform_group.add(PLATFORM2)
		self.platform_group.add(PLATFORM3)
		self.platform_group.add(PLATFORM4)
		self.game_state.init_platform_group(self.platform_group)

		INV_FULL_POPUP_SURFACE = game.load_picture(os.path.join(IMAGE_UI_PATH, "inventory_full.png"), True)
		self.inv_full_popup = ui.FadeDisplay(self.screen, (0, 0), INV_FULL_POPUP_SURFACE, 2000, 255, -10, (2, 1.5))
		EXHAUSETED_POPUP_SURFACE = game.load_picture(os.path.join(IMAGE_UI_PATH, "exhausted.png"), True)
		self.exhausted_popup = ui.FadeDisplay(self.screen, (0,0), EXHAUSETED_POPUP_SURFACE, 2000, 255, -10, (2, 1.5))

		# Create player and animation
		ANIMATION_DICT = {
			game.PlayerSprite.AnimationState.IDLE: game.PlayerSprite.AnimationData(0, 3, 200, True, True, 0),
			game.PlayerSprite.AnimationState.WALK: game.PlayerSprite.AnimationData(3, 3, 150, True, True, 0), 
			game.PlayerSprite.AnimationState.JUMP: game.PlayerSprite.AnimationData(10, 3, 100, False, True, 3),
			game.PlayerSprite.AnimationState.WALL_JUMP: game.PlayerSprite.AnimationData(10, 3, 140, False, False, 3),
			game.PlayerSprite.AnimationState.WALL_SLIDE: game.PlayerSprite.AnimationData(9, 1, 200, True, False, 2),
			game.PlayerSprite.AnimationState.FALL: game.PlayerSprite.AnimationData(12, 1, 300, True, True, 1),
			game.PlayerSprite.AnimationState.DIG: game.PlayerSprite.AnimationData(6, 3, 100, False, True, 3)
		}
		PLAYER_SURFACE = game.load_picture(os.path.join(IMAGE_MAIN_PATH, "player_anim.png"), True)
		
		self.player = game.PlayerSprite(START_POS, PLAYER_HITBLOCK_SIZE, self.player_stats, self.game_state).init_screen(self.screen).init_image_offset(PLAYER_IMAGE_OFFSET) \
				.init_animation_data(ANIMATION_DICT)
		self.player.set_surface(PLAYER_SURFACE, PLAYER_SURFACE_SIZE, PLAYER_SURFACE_SCALE)
		self.player.check_init()
		
		self.camera = game.Camera(START_POS)
		
		self.rhythm_handler = game.RhythmHandler(os.path.join(MUSIC_PATH, "loudness_log.txt"), RHYTHM_ERROR_MARGIN_MS, RHYTHM_BAR_WIDTH, RHYTHM_BAR_HEIGHT, RHYTHM_SHOW_LENGTH_MS, WRONG_PRESS_COOLDOWN_MS) \
						.init_screen(self.screen, RHYTHM_BAR_LINE_RATIO, (SCREEN_WIDTH_HALF, SCREEN_HEIGHT - 30))
		self.rhythm_handler.check_init()
		
		SHOP_SCALE = SCREEN_WIDTH / SCREEN_HEIGHT * 10 if FULL_SCREEN else 10
		SHOP_SURFACE = game.load_picture(os.path.join(IMAGE_MAIN_PATH, "Tavern.png"), True)
		SHOP_SIZE = SHOP_SURFACE.get_rect().size
		SHOP_SURFACE = pygame.transform.scale(SHOP_SURFACE, (SHOP_SIZE[0] * SHOP_SCALE, SHOP_SIZE[1] * SHOP_SCALE))

		self.shop = game.PlatformSprite(SHOP_SURFACE, (0, 0))
		self.shop.get_rect().bottomleft = (MINE_POS[0] + BLOCK_WIDTH * (BLOCK_PER_WIDTH + 2), MINE_POS[1])				

		BAR_POS_X = round(SCREEN_WIDTH*0.1)
		base_surf = game.load_picture(os.path.join(IMAGE_UI_PATH, "base_bar.png"), True)		
		border_surf = game.load_picture(os.path.join(IMAGE_UI_PATH, "base_border.png"), True)
		hp_over_surf = game.load_picture(os.path.join(IMAGE_UI_PATH, "health_bar.png"), True)
		hp_icon_surf = game.load_picture(os.path.join(IMAGE_UI_PATH, "health_icon.png"), True)
		energy_over_surf = game.load_picture(os.path.join(IMAGE_UI_PATH, "energy_bar.png"), True)		
		energy_icon_surf = game.load_picture(os.path.join(IMAGE_UI_PATH, "energy_icon.png"), True)
		stash_over_surf = game.load_picture(os.path.join(IMAGE_UI_PATH, "stash_bar.png"), True)
		stash_icon_surf = game.load_picture(os.path.join(IMAGE_UI_PATH, "stash_icon.png"), True)
		money_icon_surf = game.load_picture(os.path.join(IMAGE_UI_PATH, "gem_icon.png"), True)	

		self.hp_bar = ui.Bar(self.screen, base_surf, hp_over_surf, border_surf, hp_icon_surf, (BAR_POS_X, round(SCREEN_HEIGHT * 0.05)), BAR_SCALE, ICON_SCALE)
		self.energy_bar = ui.Bar(self.screen, base_surf, energy_over_surf, border_surf, energy_icon_surf, (BAR_POS_X, round(SCREEN_HEIGHT * 0.13)), BAR_SCALE, ICON_SCALE)
		self.stash_bar = ui.Bar(self.screen, base_surf, stash_over_surf, border_surf, stash_icon_surf, (BAR_POS_X, round(SCREEN_HEIGHT * 0.21)), BAR_SCALE, ICON_SCALE)

		self.money_icon = ui.ScalableDisplay(self.screen, (round(SCREEN_WIDTH * 0.87),round(SCREEN_HEIGHT * 0.07)), money_icon_surf, ICON_SCALE)

		self.bar_font = pygame.font.Font(os.path.join(FONT_PATH, "Tiny5.ttf"), round(SCREEN_WIDTH/SCREEN_HEIGHT * 11.25) if FULL_SCREEN else 15)
		self.font = pygame.font.Font(os.path.join(FONT_PATH, "Tiny5.ttf"), round(SCREEN_WIDTH/SCREEN_HEIGHT * 21.25) if FULL_SCREEN else 25)
		

	def start(self):
		super().start()

		game.reset(self.player_stats, self.game_state, self.player)
		try:
			game.load_game(AUTO_SAVE_FILE_NAME, self.player_stats, self.game_state, self.player)
		except FileNotFoundError as e:
			print(str(e))
		
		self.rhythm_handler.start(os.path.join(MUSIC_PATH, r"separated\htdemucs\bad_apple\drums.flac"), 0.5)


	def run_loop(self):
		super().run_loop()
		events = pygame.event.get()
		pressed_dig = False
		for event in events:
			if event.type == pygame.QUIT:
				self.scene_manager.stop()
				return
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					self.scene_manager.change_scene(PAUSE_SCENE_KEY)
					return
				if event.key in (pygame.K_j, pygame.K_k):
					pressed_dig = True

		self.screen.fill("#434389")
		
		keys = pygame.key.get_pressed()

		self.rhythm_handler.update(self.player, pressed_dig)

		self.player.handle_movement(keys, events, self.dt)
		self.player.update_position_and_collision(self.dt)
		try:
			self.player.handle_break_block(keys, events, self.game_state)
		except ValueError as e:
			if str(e) == "Inventory full":
				self.inv_full_popup.trigger()
			elif str(e) == "Energy not enough":
				self.exhausted_popup.trigger()
		if self.player_stats.game_over:
			self.scene_manager.change_scene(GAME_OVER_KEY, reset_stack=True)
			return
		
		# Update camera movement
		player_rect = self.player.get_rect()
		if player_rect.y > TRANSITION_SCENE_POSITION_Y:
			player_rect.y = NEW_SCENE_POSITION_Y
			self.player.velocity_y = 0
			self.camera.y = NEW_SCENE_POSITION_Y
			self.player_stats.scene_finished_amount += 1
			self.game_state.increase_map_difficulty()
			self.game_state.random_seed()
			self.game_state.reset_block_broken()
		
		self.camera.update(player_rect, self.dt)

		if pressed_dig and self.shop.get_rect().colliderect(self.player.get_rect()):
			self.scene_manager.change_scene(BAR_SCENE_KEY)
			return

		# --- DRAWING ---
		cam_offset = self.camera.get_cam_offset()

		self.inv_full_popup.rect.centerx = self.player.get_rect().centerx + cam_offset[0]
		self.inv_full_popup.rect.centery = self.player.get_rect().centery + cam_offset[1] - 50
		self.exhausted_popup.rect.centerx = self.player.get_rect().centerx + cam_offset[0]
		self.exhausted_popup.rect.centery = self.player.get_rect().centery + cam_offset[1] - 50

		self.screen.blit(self.underground_surface, (round(MINE_POS[0] + cam_offset[0]), round(MINE_POS[1] + cam_offset[1])))

		for block in self.game_state.get_block_group():
			if block.image == None:
				raise TypeError("'image' variable cannot be None type.")
			self.screen.blit(block.image, (round(block.get_rect().x + cam_offset[0]), round(block.get_rect().y + cam_offset[1])))
			if block.damage_taken > 0:
				break_level = math.floor(block.damage_taken / block.max_health * BREAK_EFFECT_LENGTH)
				temp_surf = game.get_surface_from_sprite_sheet(self.break_effect_sheet, (break_level, 0), (BREAK_EFFECT_WIDTH, BREAK_EFFECT_WIDTH), block.get_rect().size[0] / BREAK_EFFECT_WIDTH, True)
				self.screen.blit(temp_surf, (round(block.get_rect().x + cam_offset[0]), round(block.get_rect().y + cam_offset[1])))

		for platform in self.platform_group:
			if platform.image == None:
				raise TypeError("'image' variable cannot be None type.")
			self.screen.blit(platform.image, (round(platform.get_rect().x + cam_offset[0]), round(platform.get_rect().y + cam_offset[1])))

		if self.shop.image == None:
			raise TypeError("'image' variable cannot be None type.")
		self.screen.blit(self.shop.image, (round(self.shop.get_rect().x + cam_offset[0]), round(self.shop.get_rect().y + cam_offset[1])))

		self.player.draw(cam_offset)

		self.rhythm_handler.draw()

		self.inv_full_popup.draw()
		self.exhausted_popup.draw()

		hp_info_text = f"HP : {self.player_stats.health}/{self.player_stats.max_health}"
		energy_info_text = f"ENERGY : {self.player_stats.energy}/{self.player_stats.max_energy}"
		stash_info_text = f"INV : {self.player_stats.block}/{self.player_stats.max_block}"
		money_info_text = f"{self.player_stats.money}"
		
		hp_info_surf = self.bar_font.render(hp_info_text, True, WHITE)
		energy_info_surf = self.bar_font.render(energy_info_text, True, WHITE)
		stash_info_surf = self.bar_font.render(stash_info_text, True, WHITE)
		money_info_surf = self.font.render(money_info_text, True, WHITE)
		
		hp_ratio = game.clamp(self.player_stats.health / self.player_stats.max_health, 0, 1)
		energy_ratio = game.clamp(self.player_stats.energy / self.player_stats.max_energy, 0, 1)
		stash_ratio = game.clamp(self.player_stats.block / self.player_stats.max_block, 0, 1)
		
		self.hp_bar.draw(self.player_stats, hp_ratio, hp_info_surf)
		self.energy_bar.draw(self.player_stats, energy_ratio, energy_info_surf)
		self.stash_bar.draw(self.player_stats, stash_ratio, stash_info_surf)
		self.money_icon.draw()
		self.screen.blit(money_info_surf, (round(SCREEN_WIDTH * 0.92),round(SCREEN_HEIGHT * 0.05)))

		pygame.display.flip()

		self.dt = self.clock.tick(FPS) / 1000
		self.dt = min(self.dt, 1 / FPS)

	def pause(self):
		super().pause()
		self.rhythm_handler.pause()

	def unpause(self):
		super().unpause()
		self.rhythm_handler.unpause()

	def stop(self):
		super().stop()
		self.rhythm_handler.stop()
		if not self.player_stats.game_over:
			game.save_game(AUTO_SAVE_FILE_NAME, self.player_stats, self.game_state, self.player)
		else:
			game.delete_save(AUTO_SAVE_FILE_NAME)
		game.reset(self.player_stats, self.game_state, self.player)

class ShopScene(Scene):
	SHOVEL_START_COST = 25
	STASH_START_COST = 15
	ENERGY_START_COST = 20
	HEALTH_START_COST = 45
	ITEM_COST_MULTIPLIER = 0.75
	SHOVEL_NAME_TEXT = "Shovel Upgrade"
	SHOVEL_INFO_TEXT = "+1 Break Damage"
	STASH_NAME_TEXT = "Inventory Upgrade"
	STASH_INFO_TEXT = "+30 Bag Slot"
	ENERGY_NAME_TEXT = "Max Energy Upgrade"
	ENERGY_INFO_TEXT = "+20 Max Energy"
	HP_NAME_TEXT = "Max Health UP"
	HP_INFO_TEXT = "+1 Max HP"
	
	def __init__(self, screen: pygame.Surface, scene_manager: SceneManager, player_stats: game.PlayerStats):
		super().__init__(screen, scene_manager)
		self.player_stats = player_stats
		LEAVE_X = SCREEN_WIDTH * 0.9375
		LEAVE_Y = SCREEN_HEIGHT * 0.9583
		UP_X = SCREEN_WIDTH * 0.0225
		UP2_X = SCREEN_WIDTH * 0.18625
		UP3_X = SCREEN_WIDTH * 0.35
		UP4_X = SCREEN_WIDTH * 0.51375
		UP_Y = SCREEN_HEIGHT * 0.285
		self.NAME_POS = (SCREEN_WIDTH * 0.375, SCREEN_HEIGHT * 0.675)
		self.INFO_POS = (SCREEN_WIDTH * 0.375 , SCREEN_HEIGHT * 0.74)
		
		BUTTON_SCALE = SCREEN_WIDTH / SCREEN_HEIGHT * 4 if FULL_SCREEN else 4
		UP_SCALE = SCREEN_WIDTH / SCREEN_HEIGHT * 0.15 if FULL_SCREEN else 0.1
		WRAPLENGTH = 300

		self.bar_font = pygame.font.Font(os.path.join(FONT_PATH, "Tiny5.ttf"), round(SCREEN_WIDTH/SCREEN_HEIGHT * 16.25) if FULL_SCREEN else 20)
		self.font = pygame.font.Font(os.path.join(FONT_PATH, "Tiny5.ttf"), round(SCREEN_WIDTH/SCREEN_HEIGHT * 26.25) if FULL_SCREEN else 30)
		self.money_font = pygame.font.Font(os.path.join(FONT_PATH, "Tiny5.ttf"), round(SCREEN_WIDTH/SCREEN_HEIGHT * 21.25) if FULL_SCREEN else 25)

		dealer_surf = game.load_picture(os.path.join(IMAGE_UI_PATH, "dealer.png"), True)
		shovel_up_surf = game.load_picture(os.path.join(IMAGE_ITEM_PATH, "dig_up.png"), True)
		shovel_over_surf = game.load_picture(os.path.join(IMAGE_ITEM_PATH, "dig_up_over.png"), True)
		energy_surf = game.load_picture(os.path.join(IMAGE_ITEM_PATH, "energy_up.png"), True)
		energy_over_surf = game.load_picture(os.path.join(IMAGE_ITEM_PATH, "energy_up_over.png"), True)
		stash_surf = game.load_picture(os.path.join(IMAGE_ITEM_PATH, "stash_up.png"), True)
		stash_over_surf = game.load_picture(os.path.join(IMAGE_ITEM_PATH, "stash_up_over.png"), True)
		hp_surf = game.load_picture(os.path.join(IMAGE_ITEM_PATH, "health_up.png"), True)
		hp_over_surf = game.load_picture(os.path.join(IMAGE_ITEM_PATH, "health_up_over.png"), True)
		leave_surf = self.font.render("Leave →", True, WHITE, BLACK, WRAPLENGTH)
		leave_over_surf = self.font.render("Leave →", True, BLACK, WHITE, WRAPLENGTH)

		shovel_button = ui.ScalableButton(screen, (round(UP_X), round(UP_Y)), shovel_up_surf, shovel_over_surf, UP_SCALE, "topleft")
		stash_button = ui.ScalableButton(screen, (round(UP2_X), round(UP_Y)), stash_surf, stash_over_surf, UP_SCALE, "topleft")
		energy_button = ui.ScalableButton(screen, (round(UP3_X), round(UP_Y)), energy_surf, energy_over_surf, UP_SCALE, "topleft")
		max_hp_button = ui.ScalableButton(screen, (round(UP4_X), round(UP_Y)), hp_surf, hp_over_surf, UP_SCALE, "topleft")
		leave_button = ui.ScalableButton(self.screen, (round(LEAVE_X), round(LEAVE_Y)), leave_surf, leave_over_surf, anchor= "bottomright")
		
		DEALER_POS = (round(SCREEN_WIDTH * 0.95625), round(SCREEN_HEIGHT * 0.167)) if FULL_SCREEN else (765, 70)
		DEALER_SCALE = (SCREEN_WIDTH / SCREEN_HEIGHT * 0.35) if FULL_SCREEN else 0.35

		dealer = ui.ScalableDisplay(screen, DEALER_POS, dealer_surf, DEALER_SCALE, "topright")
		
		UI_BG_SCALE = SCREEN_WIDTH / SCREEN_HEIGHT * 1.33 if FULL_SCREEN else 1
		UI_BG_SIZE_X = 500 * UI_BG_SCALE
		UI_BG_SIZE_Y = 110 * UI_BG_SCALE
		
		self.ui_bg = pygame.Surface((UI_BG_SIZE_X, UI_BG_SIZE_Y))
		self.ui_bg.fill(BLACK)
		self.ui_bg_border = pygame.Surface((UI_BG_SIZE_X + 7, UI_BG_SIZE_Y + 7))
		self.ui_bg_border.fill(WHITE)

		self.ui_bg_rect = self.ui_bg.get_rect(topleft=(SCREEN_WIDTH*0.06,SCREEN_HEIGHT*0.64))
		self.ui_bg_border_rect = self.ui_bg_border.get_rect(center = self.ui_bg_rect.center)

		money_icon_surf = game.load_picture(os.path.join(IMAGE_UI_PATH, "gem_icon.png"), True)
		self.money_icon = ui.ScalableDisplay(self.screen, (round(SCREEN_WIDTH * 0.87),round(SCREEN_HEIGHT * 0.07)), money_icon_surf, ICON_SCALE)
		
		self.shop_group = ui.UIGroup({
			"leave": leave_button,
			"shovel": shovel_button,  
			"dealer": dealer,
			"stash": stash_button, 
			"energy": energy_button,
			"max_hp": max_hp_button
		})

	def run_loop(self):
		super().run_loop()
		events = pygame.event.get()
		
		mouse_pos = pygame.mouse.get_pos()
		keys = pygame.key.get_pressed()
		clicked = self.shop_group.update(mouse_pos, events)
		
		self.screen.fill("#000000")
		
		for event in events:
			if event.type == pygame.QUIT:
				self.scene_manager.stop()
				return
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					self.scene_manager.go_back()
					return
		
		if clicked["leave"]:
			self.scene_manager.go_back()
			return

		cost_multiplier = (1 + self.player_stats.scene_finished_amount * ShopScene.ITEM_COST_MULTIPLIER)
		draw_text_info = False
		name_surf = self.font.render("", True, WHITE)
		name_rect = name_surf.get_rect(center = self.NAME_POS)
		info_surf = self.bar_font.render("", True, WHITE)
		info_rect = info_surf.get_rect(center = self.INFO_POS)
		if isinstance(self.shop_group.ui_dict["shovel"], ui.ScalableButton) and self.shop_group.ui_dict["shovel"].activated:
			name_surf = self.font.render(ShopScene.SHOVEL_NAME_TEXT, True, WHITE)
			name_rect = name_surf.get_rect(center = self.NAME_POS)
			info_surf = self.bar_font.render(f"{ShopScene.SHOVEL_INFO_TEXT}\ncost: {round(ShopScene.SHOVEL_START_COST * cost_multiplier)}", True, WHITE)
			info_rect = info_surf.get_rect(center = self.INFO_POS)
			draw_text_info = True

		if isinstance(self.shop_group.ui_dict["stash"], ui.ScalableButton) and self.shop_group.ui_dict["stash"].activated:
			name_surf = self.font.render(ShopScene.STASH_NAME_TEXT, True, WHITE)
			name_rect = name_surf.get_rect(center = self.NAME_POS)
			info_surf = self.bar_font.render(f"{ShopScene.STASH_INFO_TEXT}\ncost: {round(ShopScene.STASH_START_COST * cost_multiplier)}", True, WHITE)
			info_rect = info_surf.get_rect(center = self.INFO_POS)
			draw_text_info = True

		if isinstance(self.shop_group.ui_dict["energy"], ui.ScalableButton) and self.shop_group.ui_dict["energy"].activated:
			name_surf = self.font.render(ShopScene.ENERGY_NAME_TEXT, True, WHITE)
			name_rect = name_surf.get_rect(center = self.NAME_POS)
			info_surf = self.bar_font.render(f"{ShopScene.ENERGY_INFO_TEXT}\ncost: {round(ShopScene.ENERGY_START_COST * cost_multiplier)}", True, WHITE)
			info_rect = info_surf.get_rect(center = self.INFO_POS)
			draw_text_info = True
		
		if isinstance(self.shop_group.ui_dict["max_hp"], ui.ScalableButton) and self.shop_group.ui_dict["max_hp"].activated:
			name_surf = self.font.render(ShopScene.HP_NAME_TEXT, True, WHITE)
			name_rect = name_surf.get_rect(center = self.NAME_POS)
			info_surf = self.bar_font.render(f"{ShopScene.HP_INFO_TEXT}\ncost: {round(ShopScene.HEALTH_START_COST * cost_multiplier)}", True, WHITE)
			info_rect = info_surf.get_rect(center = self.INFO_POS)
			draw_text_info = True

		if clicked["shovel"]:
			self.player_stats.handle_bulk_buy(keys, round(ShopScene.SHOVEL_START_COST * cost_multiplier), lambda: setattr(self.player_stats, "break_damage", self.player_stats.break_damage + 1))

		if clicked["max_hp"]:
			self.player_stats.handle_bulk_buy(keys, round(ShopScene.HEALTH_START_COST * cost_multiplier), lambda: setattr(self.player_stats, "max_health", self.player_stats.max_health + 1))
				
		
		if clicked["stash"]:
			self.player_stats.handle_bulk_buy(keys, round(ShopScene.STASH_START_COST * cost_multiplier), lambda: setattr(self.player_stats, "max_block", self.player_stats.max_block + 30))
		
		if clicked["energy"]:
			self.player_stats.handle_bulk_buy(keys, round(ShopScene.ENERGY_START_COST * cost_multiplier), lambda: setattr(self.player_stats, "max_energy", self.player_stats.max_energy + 20))
		
		self.shop_group.draw()

		money_info_text = f"{self.player_stats.money}"
		money_info_surf = self.money_font.render(money_info_text, True, WHITE)
		player_info = f"HP : {self.player_stats.max_health}\nDMG : {self.player_stats.break_damage}\nENERGY : {self.player_stats.max_energy}\nINV : {self.player_stats.max_block}"
		player_info_surf = self.font.render(player_info, True, WHITE)
		player_info_rect = player_info_surf.get_rect(topleft = PLAYER_INFO_POS)
		
		if draw_text_info:
			self.screen.blit(self.ui_bg_border, self.ui_bg_border_rect)
			self.screen.blit(self.ui_bg, self.ui_bg_rect)
			self.screen.blit(name_surf, name_rect)
			self.screen.blit(info_surf, info_rect)

		self.screen.blit(player_info_surf, player_info_rect)

		self.money_icon.draw()
		self.screen.blit(money_info_surf, (round(SCREEN_WIDTH * 0.92),round(SCREEN_HEIGHT * 0.05)))
						
		pygame.display.flip()

		self.dt = self.clock.tick(FPS_UI) / 1000
		self.dt = min(self.dt, 1 / FPS_UI)

class BarScene(Scene):
	ENERGY_REFILL_COST = 10
	HEALTH_REFILL_COST = 55
	REFILL_COST_MULTIPLIER = 0.8
	def __init__(self, screen: pygame.Surface, scene_manager: SceneManager, player_stats: game.PlayerStats):
		super().__init__(screen, scene_manager)
		self.player_stats = player_stats

		BAR_POS_X = round(SCREEN_WIDTH*0.1)

		base_surf = game.load_picture(os.path.join(IMAGE_UI_PATH, "base_bar.png"), True)		
		border_surf = game.load_picture(os.path.join(IMAGE_UI_PATH, "base_border.png"), True)
		hp_over_surf = game.load_picture(os.path.join(IMAGE_UI_PATH, "health_bar.png"), True)
		hp_icon_surf = game.load_picture(os.path.join(IMAGE_UI_PATH, "health_icon.png"), True)
		energy_over_surf = game.load_picture(os.path.join(IMAGE_UI_PATH, "energy_bar.png"), True)		
		energy_icon_surf = game.load_picture(os.path.join(IMAGE_UI_PATH, "energy_icon.png"), True)
		stash_over_surf = game.load_picture(os.path.join(IMAGE_UI_PATH, "stash_bar.png"), True)
		stash_icon_surf = game.load_picture(os.path.join(IMAGE_UI_PATH, "stash_icon.png"), True)

		self.hp_bar = ui.Bar(self.screen, base_surf, hp_over_surf, border_surf, hp_icon_surf, (BAR_POS_X, round(SCREEN_HEIGHT*0.05)), BAR_SCALE, ICON_SCALE)
		self.energy_bar = ui.Bar(self.screen, base_surf, energy_over_surf, border_surf, energy_icon_surf, (BAR_POS_X, round(SCREEN_HEIGHT*0.13)), BAR_SCALE, ICON_SCALE)
		self.stash_bar = ui.Bar(self.screen, base_surf, stash_over_surf, border_surf, stash_icon_surf, (BAR_POS_X, round(SCREEN_HEIGHT*0.21)), BAR_SCALE, ICON_SCALE)	

		self.bar_font = pygame.font.Font(os.path.join(FONT_PATH, "Tiny5.ttf"), round(SCREEN_WIDTH/SCREEN_HEIGHT * 11.25) if FULL_SCREEN else 15)
		self.font = pygame.font.Font(os.path.join(FONT_PATH, "Tiny5.ttf"), round(SCREEN_WIDTH/SCREEN_HEIGHT * 21.25) if FULL_SCREEN else 25)
		WRAPLENGTH = 300
		
		convert_surf = self.font.render("• Sell Treasures", True, WHITE, BLACK, WRAPLENGTH)
		add_energy_surf = self.font.render("• Refill Energy", True, WHITE, BLACK, WRAPLENGTH)
		shop_surf = self.font.render("• Buy Upgrade", True, WHITE, BLACK, WRAPLENGTH)
		leave_surf = self.font.render("Leave →", True, WHITE, BLACK, WRAPLENGTH)
		add_health_surf = self.font.render("• Heal", True, WHITE, BLACK, WRAPLENGTH)		

		convert_over_surf = self.font.render("• Sell Treasures", True, BLACK, WHITE, WRAPLENGTH)
		add_energy_over_surf = self.font.render("• Refill Energy", True, BLACK, WHITE, WRAPLENGTH)
		shop_over_surf = self.font.render("• Buy Upgrade", True, BLACK, WHITE, WRAPLENGTH)
		leave_over_surf = self.font.render("Leave →", True, BLACK, WHITE, WRAPLENGTH)
		add_health_over_surf = self.font.render("• Heal", True, BLACK, WHITE, WRAPLENGTH)
		money_icon_surf = game.load_picture(os.path.join(IMAGE_UI_PATH, "gem_icon.png"), True)	

		BUTTON_X_1 = round(SCREEN_WIDTH / 3.5) if FULL_SCREEN else round(SCREEN_WIDTH / 4.5)
		BUTTON_X_2 = round(SCREEN_WIDTH / 1.85)
		BUTTON_Y_1 = round(SCREEN_HEIGHT * 0.65)
		BUTTON_Y_2 = round(SCREEN_HEIGHT * 0.75)
		LEAVE_X = round(SCREEN_WIDTH / 1.465)
		LEAVE_Y = round(SCREEN_HEIGHT * 0.85)
		UI_BG_SCALE = round(SCREEN_WIDTH / SCREEN_HEIGHT * 1.4) if FULL_SCREEN else 1
		UI_BG_SIZE_X = 500 * UI_BG_SCALE
		UI_BG_SIZE_Y = 200 * UI_BG_SCALE
		
		self.ui_bg = pygame.Surface((UI_BG_SIZE_X, UI_BG_SIZE_Y))
		self.ui_bg.fill(BLACK)
		self.ui_bg_border = pygame.Surface((UI_BG_SIZE_X + 7, UI_BG_SIZE_Y + 7))
		self.ui_bg_border.fill(WHITE)
		self.ui_bg_rect = self.ui_bg.get_rect(center=(SCREEN_WIDTH_HALF,SCREEN_HEIGHT*0.75))
		self.ui_bg_border_rect = self.ui_bg_border.get_rect(center = self.ui_bg_rect.center)
		convert_button = ui.ScalableButton(self.screen, (BUTTON_X_1, BUTTON_Y_1), convert_surf, convert_over_surf, anchor= "topleft")
		shop_button = ui.ScalableButton(self.screen, (BUTTON_X_2, BUTTON_Y_1), shop_surf, shop_over_surf, anchor= "topleft")
		add_energy_button = ui.ScalableButton(self.screen, (BUTTON_X_2, BUTTON_Y_2), add_energy_surf, add_energy_over_surf, anchor= "topleft")
		add_health_button = ui.ScalableButton(self.screen, (BUTTON_X_1, BUTTON_Y_2), add_health_surf, add_health_over_surf, anchor= "topleft")
		leave_button = ui.ScalableButton(self.screen, (LEAVE_X, LEAVE_Y), leave_surf, leave_over_surf, anchor= "topleft")
		self.money_icon = ui.ScalableDisplay(self.screen, (round(SCREEN_WIDTH * 0.87),round(SCREEN_HEIGHT * 0.07)), money_icon_surf, ICON_SCALE)
			

		self.bar_group = ui.UIGroup({
			"convert": convert_button, 
			"add_energy": add_energy_button, 
			"shop": shop_button, 
			"leave": leave_button, 
			"add_health": add_health_button
		})

		
		
	def run_loop(self):
		super().run_loop()
		events = pygame.event.get()
		mouse_pos = pygame.mouse.get_pos()
	
		clicked = self.bar_group.update(mouse_pos, events)
		
		self.screen.fill("#2C1601")
		for event in events:
			if event.type == pygame.QUIT:
				self.scene_manager.stop()
				return
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					self.scene_manager.go_back()
					return

		cost_multiplier = (1 + self.player_stats.scene_finished_amount * BarScene.REFILL_COST_MULTIPLIER)
		if clicked["convert"]:
			self.player_stats.convert_block_to_money()

		if clicked["add_energy"]:
			if self.player_stats.buy(round(BarScene.ENERGY_REFILL_COST * cost_multiplier)):
				self.player_stats.refill_energy()

		if clicked["shop"]:
			self.scene_manager.change_scene(SHOP_SCENE_KEY)

		if clicked["leave"]:
			self.scene_manager.go_back()

		if clicked["add_health"]:
			if self.player_stats.buy(round(BarScene.HEALTH_REFILL_COST * cost_multiplier)):
				self.player_stats.refill_health()

		self.screen.blit(self.ui_bg_border, self.ui_bg_border_rect)
		self.screen.blit(self.ui_bg, self.ui_bg_rect)
		self.bar_group.draw()

		hp_info_text = f"HP : {self.player_stats.health}/{self.player_stats.max_health}"
		energy_info_text = f"ENERGY : {self.player_stats.energy}/{self.player_stats.max_energy}"
		stash_info_text = f"INV : {self.player_stats.block}/{self.player_stats.max_block}"
		money_info_text = f"{self.player_stats.money}"
		
		hp_info_surf = self.bar_font.render(hp_info_text, True, WHITE)
		energy_info_surf = self.bar_font.render(energy_info_text, True, WHITE)
		stash_info_surf = self.bar_font.render(stash_info_text, True, WHITE)
		money_info_surf = self.font.render(money_info_text, True, WHITE)
		
		hp_ratio = game.clamp(self.player_stats.health / self.player_stats.max_health, 0, 1)
		energy_ratio = game.clamp(self.player_stats.energy / self.player_stats.max_energy, 0, 1)
		stash_ratio = game.clamp(self.player_stats.block / self.player_stats.max_block, 0, 1)
		
		self.hp_bar.draw(self.player_stats, hp_ratio, hp_info_surf)
		self.energy_bar.draw(self.player_stats, energy_ratio, energy_info_surf)
		self.stash_bar.draw(self.player_stats, stash_ratio, stash_info_surf)
	
		self.money_icon.draw()
		self.screen.blit(money_info_surf, (round(SCREEN_WIDTH * 0.92),round(SCREEN_HEIGHT * 0.05)))


		pygame.display.flip()

		self.dt = self.clock.tick(FPS_UI) / 1000
		self.dt = min(self.dt, 1 / FPS_UI)

class GameOverScene(Scene):
	PLAY_BUTTON = "play"
	EXIT_BUTTON = "exit"
	LOGO_DISPLAY = "logo"
	EXIT_DESKTOP = "exit_desktop"
	def __init__(self, screen: pygame.Surface, scene_manager: SceneManager, player_stats: game.PlayerStats):
		super().__init__(screen, scene_manager)

		PLAY_BTN_Y = round(SCREEN_HEIGHT / 1.75)
		EXIT_BTN_Y = round(SCREEN_HEIGHT / 1.45)
		LOGO_Y = round(SCREEN_HEIGHT / 2.85)
		BUTTON_SCALE = SCREEN_WIDTH / SCREEN_HEIGHT * 4 if FULL_SCREEN else 4
		EXIT_DESKTOP_Y = round(SCREEN_HEIGHT / 1.225)
		LOGO_SCALE = SCREEN_WIDTH / SCREEN_HEIGHT * 2 if FULL_SCREEN else 2

		# Main Menu
		play_up_surf = game.load_picture(os.path.join(IMAGE_UI_PATH, "new_game.png"), True)
		play_over_surf = game.load_picture(os.path.join(IMAGE_UI_PATH, 'new_game_over.png'), True)
		exit_up_surf = game.load_picture(os.path.join(IMAGE_UI_PATH, "exit.png"), True)
		exit_over_surf = game.load_picture(os.path.join(IMAGE_UI_PATH, "exit_over.png"), True)
		logo_surf = game.load_picture(os.path.join(IMAGE_UI_PATH, "game_over_logo.png"), True)
		exit_desktop_surf = game.load_picture(os.path.join(IMAGE_UI_PATH, "exit_to_desktop.png"), True)
		exit_desktop_over_surf = game.load_picture(os.path.join(IMAGE_UI_PATH, "exit_to_desktop_over.png"), True)
		
		# Main Menu Button
		play_button = ui.ScalableButton(screen, (SCREEN_WIDTH_HALF, PLAY_BTN_Y), play_up_surf, play_over_surf, BUTTON_SCALE)
		exit_button = ui.ScalableButton(screen, (SCREEN_WIDTH_HALF, EXIT_BTN_Y), exit_up_surf, exit_over_surf, BUTTON_SCALE)
		logo = ui.ScalableDisplay(screen, (SCREEN_WIDTH_HALF, LOGO_Y), logo_surf, LOGO_SCALE)
		exit_desktop_button = ui.ScalableButton(screen, (SCREEN_WIDTH_HALF, EXIT_DESKTOP_Y), exit_desktop_surf, exit_desktop_over_surf, BUTTON_SCALE)
			
		self.main_menu_group = ui.UIGroup({ 
			GameOverScene.PLAY_BUTTON: play_button, 
			GameOverScene.EXIT_BUTTON: exit_button,
			GameOverScene.LOGO_DISPLAY: logo,
			GameOverScene.EXIT_DESKTOP: exit_desktop_button
		})

	def run_loop(self):
		super().run_loop()
		events = pygame.event.get()
		for event in events:
			if event.type == pygame.QUIT:
				self.scene_manager.stop()
				return

		self.screen.fill("#DA3131")

		mouse_pos = pygame.mouse.get_pos()
		clicked = self.main_menu_group.update(mouse_pos, events)

		if clicked[GameOverScene.PLAY_BUTTON]:
			self.scene_manager.change_scene(MAIN_SCENE_KEY, reset_stack=True)
			return

		if clicked[GameOverScene.EXIT_BUTTON]:
			self.scene_manager.change_scene(MAIN_MENU_SCENE_KEY, reset_stack=True)
			return

		if clicked[GameOverScene.EXIT_DESKTOP]:
			self.scene_manager.stop()
			return

		self.main_menu_group.draw()
		 
		pygame.display.flip()

		self.dt = self.clock.tick(FPS_UI) / 1000
		self.dt = min(self.dt, 1 / FPS_UI)


if __name__ == "__main__":
	main()