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

	player_stats = game.PlayerStats().init_break_damage(START_BREAK_DAMAGE, START_BREAK_DAMAGE_MODIFIER).init_max_block(START_MAX_INVENTORY) \
				.init_max_energy(START_ENERGY).init_max_health(START_HEALTH).init_on_beat_constant(START_ON_BEAT_EXTRA_DMG, START_ON_BEAT_EXTRA_DMG_MODIFIER) \
				.init_rate_of_convertion(START_RATE_OF_CONVERTION)
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

		PLAY_BTN_Y = round(SCREEN_HEIGHT / 1.55)
		EXIT_BTN_Y = round(SCREEN_HEIGHT / 1.325)
		LOGO_Y = round(SCREEN_HEIGHT / 2.85)
		BUTTON_SCALE = SCREEN_WIDTH / SCREEN_HEIGHT * 4 if FULL_SCREEN else 3
		LOGO_SCALE = SCREEN_WIDTH / SCREEN_HEIGHT * 0.55 if FULL_SCREEN else 0.5

		# Main Menu
		play_up_surf = game.load_picture(os.path.join(IMAGE_PATH, "play.png"), True)
		play_over_surf = game.load_picture(os.path.join(IMAGE_PATH, 'play_over.png'), True)
		exit_up_surf = game.load_picture(os.path.join(IMAGE_PATH, "exit.png"), True)
		exit_over_surf = game.load_picture(os.path.join(IMAGE_PATH, "exit_over.png"), True)
		logo_surf = game.load_picture(os.path.join(IMAGE_PATH, "logo.png"), True)
		
		# Main Menu Button
		new_game_button = ui.ScalableButton(screen, (SCREEN_WIDTH_HALF, round(SCREEN_HEIGHT / 1.775)), play_up_surf, play_over_surf, BUTTON_SCALE)
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
			pass

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

		PLAY_BTN_Y = round(SCREEN_HEIGHT / 1.55)
		EXIT_BTN_Y = round(SCREEN_HEIGHT / 1.325)
		LOGO_Y = round(SCREEN_HEIGHT / 2.85)
		BUTTON_SCALE = SCREEN_WIDTH / SCREEN_HEIGHT * 4 if FULL_SCREEN else 3
		LOGO_SCALE = SCREEN_WIDTH / SCREEN_HEIGHT * 0.55 if FULL_SCREEN else 0.5

		# Main Menu
		play_up_surf = game.load_picture(os.path.join(IMAGE_PATH, "play.png"), True)
		play_over_surf = game.load_picture(os.path.join(IMAGE_PATH, 'play_over.png'), True)
		exit_up_surf = game.load_picture(os.path.join(IMAGE_PATH, "exit.png"), True)
		exit_over_surf = game.load_picture(os.path.join(IMAGE_PATH, "exit_over.png"), True)
		logo_surf = game.load_picture(os.path.join(IMAGE_PATH, "logo.png"), True)
		
		# Main Menu Button
		play_button = ui.ScalableButton(screen, (SCREEN_WIDTH_HALF, PLAY_BTN_Y), play_up_surf, play_over_surf, BUTTON_SCALE)
		exit_button = ui.ScalableButton(screen, (SCREEN_WIDTH_HALF, EXIT_BTN_Y), exit_up_surf, exit_over_surf, BUTTON_SCALE)
		logo = ui.ScalableDisplay(screen, (SCREEN_WIDTH_HALF, LOGO_Y), logo_surf, LOGO_SCALE)
		exit_desktop_button = ui.ScalableButton(screen, (SCREEN_WIDTH_HALF, round(SCREEN_HEIGHT / 1.2)), exit_up_surf, exit_over_surf, BUTTON_SCALE)
			
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

		self.break_effect_sheet = game.load_picture(os.path.join(IMAGE_PATH, "break_effect.png"), True)
		SPRITE_SHEET_SURFACE = game.load_picture(os.path.join(IMAGE_PATH, "tiles_spritesheet.png"), True)
		# Layer 1
		BLOCK1_SURFACE_DATA = game.get_spritesheet_data(os.path.join(IMAGE_PATH, "tiles_spritesheet.txt"), "grassCenter")
		BLOCK1_SURFACE = game.get_surface_from_sprite_sheet2(SPRITE_SHEET_SURFACE, BLOCK1_SURFACE_DATA[0], BLOCK1_SURFACE_DATA[1], 1, False)
		BLOCK1_DATA = game.BlockData(BLOCK1_SURFACE, 3.0, 0.8)
		
		BLOCK2_SURFACE_DATA = game.get_spritesheet_data(os.path.join(IMAGE_PATH, "tiles_spritesheet.txt"), "stoneCenter")
		BLOCK2_SURFACE = game.get_surface_from_sprite_sheet2(SPRITE_SHEET_SURFACE, BLOCK2_SURFACE_DATA[0], BLOCK2_SURFACE_DATA[1], 1, False)
		BLOCK2_DATA = game.BlockData(BLOCK2_SURFACE, 6.0, 0.2)
		
		LAYER1_DATA = game.LayerData(10, (BLOCK1_DATA, BLOCK2_DATA)).init_bomb(0.05, 1).init_energy(0.02, 20) \
					.init_treasure(0.01, 50).init_multiblock_rate(0.01).init_energy_usage(1)
		LAYER1_DATA.check_init()
		
		
		# Layer 2
		BLOCK3_SURFACE = pygame.Surface((BLOCK_WIDTH, BLOCK_HEIGHT))
		BLOCK3_SURFACE.fill("orange")
		BLOCK3_DATA = game.BlockData(BLOCK3_SURFACE, 10.0, 0.6)
		
		BLOCK4_SURFACE = pygame.Surface((BLOCK_WIDTH, BLOCK_HEIGHT))
		BLOCK4_SURFACE.fill("pink")
		BLOCK4_DATA = game.BlockData(BLOCK4_SURFACE, 15.0, 0.4)
		
		LAYER2_DATA = game.LayerData(25, (BLOCK3_DATA, BLOCK4_DATA)).init_bomb(0.05, 2).init_energy(0.02, 30) \
					.init_treasure(0.01, 80).init_multiblock_rate(0.02).init_energy_usage(1)
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
		
		LAYER3_DATA = game.LayerData(50, (BLOCK5_DATA, BLOCK6_DATA, BLOCK7_DATA)).init_bomb(0.1, 3).init_energy(0.02, 50) \
					.init_treasure(0.015, 100).init_multiblock_rate(0.03).init_energy_usage(2)
		LAYER3_DATA.check_init()
		
		
		MAP1_DATA = game.MapData((LAYER1_DATA, LAYER2_DATA, LAYER3_DATA), BLOCK_WIDTH, BLOCK_HEIGHT)
		
		self.platform_group = pygame.sprite.Group()
		
		PLATFORM1_SURFACE = pygame.Surface((BLOCK_WIDTH * BLOCK_PER_WIDTH * 4, BLOCK_HEIGHT * BLOCK_PER_HEIGHT))
		PLATFORM1_SURFACE.fill("brown")
		PLATFORM2_SURFACE = PLATFORM1_SURFACE.copy()
		
		PLATFORM1 = game.PlatformSprite(PLATFORM1_SURFACE, (0, 0))
		PLATFORM1.get_rect().topright = MINE_POS
		
		PLATFORM2 = game.PlatformSprite(PLATFORM2_SURFACE, (MINE_POS[0] + BLOCK_WIDTH * BLOCK_PER_WIDTH, MINE_POS[1]))

		self.game_state = game.GameState(MAP1_DATA, WORLD_START_SEED)
		self.game_state.create_new_block_group()
		self.platform_group.add(PLATFORM1)
		self.platform_group.add(PLATFORM2)
		self.game_state.init_platform_group(self.platform_group)

		self.display_text1 = pygwidgets.DisplayText(self.screen, (0, 0), "Test", textColor="white", fontSize=32)
		self.display_text1.setCenteredLoc((SCREEN_WIDTH_HALF, 20))
		
		self.display_text2 = pygwidgets.DisplayText(self.screen, (0, 0), "Test", textColor="white", fontSize=32)
		self.display_text2.setCenteredLoc((SCREEN_WIDTH_HALF, SCREEN_HEIGHT - 20))

		# Create player and animation
		ANIMATION_DICT = {
			game.PlayerSprite.AnimationState.IDLE: game.PlayerSprite.AnimationData(0, 4, 150, True, 0),
			game.PlayerSprite.AnimationState.WALK: game.PlayerSprite.AnimationData(4, 6, 120, True, 0),
			game.PlayerSprite.AnimationState.JUMP: game.PlayerSprite.AnimationData(10, 4, 120, False, 3),
			game.PlayerSprite.AnimationState.WALL_JUMP: game.PlayerSprite.AnimationData(10, 4, 100, False, 3),
			game.PlayerSprite.AnimationState.WALL_SLIDE: game.PlayerSprite.AnimationData(5, 1, 200, True, 2),
			game.PlayerSprite.AnimationState.FALL: game.PlayerSprite.AnimationData(11, 3, 150, True, 1),
			game.PlayerSprite.AnimationState.DIG: game.PlayerSprite.AnimationData(17, 3, 100, False, 3)
		}
		PLAYER_SURFACE = game.load_picture(os.path.join(IMAGE_PATH, "doux.png"), True)
		
		self.player = game.PlayerSprite(START_POS, PLAYER_HITBLOCK_SIZE, self.player_stats, self.game_state).init_screen(self.screen).init_image_offset(PLAYER_IMAGE_OFFSET) \
				.init_animation_data(ANIMATION_DICT)
		self.player.set_surface(PLAYER_SURFACE, PLAYER_SURFACE_SIZE, PLAYER_SURFACE_SCALE)
		self.player.check_init()
		
		self.camera = game.Camera(START_POS)
		
		self.rhythm_handler = game.RhythmHandler(os.path.join(MUSIC_PATH, "loudness_log.txt"), RHYTHM_ERROR_MARGIN_MS, RHYTHM_BAR_WIDTH, RHYTHM_BAR_HEIGHT, RHYTHM_SHOW_LENGTH_MS, WRONG_PRESS_COOLDOWN_MS) \
						.init_screen(self.screen, RHYTHM_BAR_LINE_RATIO, (SCREEN_WIDTH_HALF, SCREEN_HEIGHT - 30))
		self.rhythm_handler.check_init()

		text_button1 = pygwidgets.TextButton(self.screen, (SCREEN_WIDTH - 100, 50), "Convert", textColor="white", fontSize=32)
		text_button2 = pygwidgets.TextButton(self.screen, (SCREEN_WIDTH - 100, 100), "+Energy", textColor="white", fontSize=32)
		
		text_button3 = pygwidgets.TextButton(self.screen, (0, 50), "Save", textColor="white", fontSize=32)
		text_button4 = pygwidgets.TextButton(self.screen, (0, 100), "Load", textColor="white", fontSize=32)
		text_button5 = pygwidgets.TextButton(self.screen, (0, 150), "Reset", textColor="white", fontSize=32)
		text_button6 = pygwidgets.TextButton(self.screen, (0, 200), "Random", textColor="white", fontSize=32)
		
		self.ui_group1 = ui.PygwidgetsUIGroup({
			"btn1": text_button1,
			"btn2": text_button2,
			"btn3":text_button3,
			"btn4":text_button4,
			"btn5":text_button5, 
			"btn6":text_button6		  
		})

		SHOP_SURFACE = pygame.Surface((BLOCK_WIDTH * 5, BLOCK_HEIGHT * 5))
		SHOP_SURFACE.fill("brown")

		self.shop = game.PlatformSprite(SHOP_SURFACE, (0, 0))
		self.shop.get_rect().bottomleft =(MINE_POS[0] + BLOCK_WIDTH * (BLOCK_PER_WIDTH + 2), MINE_POS[1])

		base_surf = pygame.Surface((300,30))
		base_surf.fill("#313030")
		hp_over_surf = pygame.Surface((300,30))
		hp_over_surf.fill("#FF0000")
		energy_over_surf = pygame.Surface((300,30))
		energy_over_surf.fill("#FFFB00")
		#base2_surf = pygame.Surface((30,300))
		#base2_surf.fill("#313030")
		stash_over_surf = pygame.Surface((30,300))
		stash_over_surf.fill("#F403FC")
		
		self.hp_bar = ui.Bar(self.screen, base_surf, hp_over_surf, (10,SCREEN_HEIGHT-250), 1)
		self.energy_bar = ui.Bar(self.screen, base_surf, energy_over_surf, (10,SCREEN_HEIGHT-210), 1)
		self.stash_bar = ui.Bar(self.screen, base_surf, stash_over_surf, (10,SCREEN_HEIGHT-170), 1)
						
	def start(self):
		super().start()

		game.reset(self.player_stats, self.game_state, self.player)
		try:
			game.load_game(AUTO_SAVE_FILE_NAME, self.player_stats, self.game_state, self.player)
		except FileNotFoundError as e:
			print(str(e))
		
		self.rhythm_handler.start(os.path.join(MUSIC_PATH, r"separated\htdemucs\bad_apple\drums.flac"), 0.7)

	def run_loop(self):
		super().run_loop()
		events = pygame.event.get()
		pressed_dig = False
		pressed_enter = False
		ui_group1_clicked = self.ui_group1.update(events)
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
				if event.key == pygame.K_RETURN:
					pressed_enter = True

		self.screen.fill("#171722")
		
		keys = pygame.key.get_pressed()
		mouse_pos = pygame.mouse.get_pos()

		self.rhythm_handler.update(self.player, pressed_dig)

		try:
			self.player.update(keys, events, self.dt, self.game_state)
		except ValueError as e:
			print(str(e))

		
		if self.player_stats.game_over:
			print("Game Over")
			self.scene_manager.change_scene(GAME_OVER_KEY, reset_stack=True)
			return
		
		# Update camera movement
		player_rect = self.player.get_rect()
		
		self.camera.update(player_rect, self.dt)
		

		self.display_text1.setText(f"Health: {self.player_stats.health}/{self.player_stats.max_health} Block: {self.player_stats.block}/{self.player_stats.max_block} Energy: {self.player_stats.energy}/{self.player_stats.max_energy} Money: {self.player_stats.money}")
		self.display_text1.setCenteredLoc((SCREEN_WIDTH_HALF, 20))

		self.display_text2.setText(f"{self.game_state.seed}")
		self.display_text2.setCenteredLoc((SCREEN_WIDTH_HALF, SCREEN_HEIGHT - 100))

		if ui_group1_clicked["btn1"]:
			self.player_stats.convert_block_to_money()

		if ui_group1_clicked["btn2"]:
			self.player_stats.refill_energy()

		if ui_group1_clicked["btn3"]:
			game.save_game(AUTO_SAVE_FILE_NAME, self.player_stats, self.game_state, self.player)

		if ui_group1_clicked["btn4"]:
			try:
				game.load_game(AUTO_SAVE_FILE_NAME, self.player_stats, self.game_state, self.player)
			except FileNotFoundError as e:
				print(str(e))

		if ui_group1_clicked["btn5"]:
			self.game_state.reset_block_broken()
			self.player_stats.reset()
			self.player.reset()

		if ui_group1_clicked["btn6"]:
			self.game_state.random_seed()
			self.game_state.create_new_block_group()

			self.game_state.reset_block_broken()
			self.player_stats.reset()

		if pressed_enter and self.shop.get_rect().colliderect(self.player.get_rect()):
			self.scene_manager.change_scene(BAR_SCENE_KEY)
			return

		# --- DRAWING ---
		cam_offset = self.camera.get_cam_offset()

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

		self.display_text1.draw()
		self.display_text2.draw()

		self.ui_group1.draw()

		hp_ratio = game.clamp(self.player_stats.health / self.player_stats.max_health, 0, 1)
		self.hp_bar.draw(self.player_stats, hp_ratio)
		energy_ratio = game.clamp(self.player_stats.energy / self.player_stats.max_energy, 0, 1)
		self.energy_bar.draw(self.player_stats, energy_ratio)
		stash_ratio = game.clamp(self.player_stats.block / self.player_stats.max_block, 0, 1)
		self.stash_bar.draw(self.player_stats, stash_ratio)
		print(stash_ratio)
		

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

class ShopScene(Scene):
	def __init__(self, screen: pygame.Surface, scene_manager: SceneManager, player_stats: game.PlayerStats):
		super().__init__(screen, scene_manager)
		self.player_stats = player_stats
		LEAVE_X = 750
		LEAVE_Y = 575
		UP_X = 53
		UP2_X = 184
		UP_Y = 40
		BUTTON_SCALE = SCREEN_WIDTH / SCREEN_HEIGHT * 4 if FULL_SCREEN else 4

		exit_up_surf = game.load_picture(os.path.join(IMAGE_PATH, "leave.png"), True)
		exit_over_surf = game.load_picture(os.path.join(IMAGE_PATH, "leave_over.png"), True)
		up1_up_surf = game.load_picture(os.path.join(IMAGE_PATH, "up1.png"), True)
		up1_over_surf = game.load_picture(os.path.join(IMAGE_PATH, "up1_over.png"), True)
		up2_up_surf = game.load_picture(os.path.join(IMAGE_PATH, "up2.png"), True)
		up2_over_surf = game.load_picture(os.path.join(IMAGE_PATH, "up2_over.png"), True)
		dealer_surf = game.load_picture(os.path.join(IMAGE_PATH, "dealer.png"), True)
		border1_surf = game.load_picture(os.path.join(IMAGE_PATH, "border1.png"), True)
		border1_surf = game.scale_surface(border1_surf, (6, 9.85))
		energy_surf = game.load_picture(os.path.join(IMAGE_PATH, "energy.png"), True)
		energy_over_surf = game.load_picture(os.path.join(IMAGE_PATH, "energy_over.png"), True)
		stash_surf = game.load_picture(os.path.join(IMAGE_PATH, "stash.png"), True)
		stash_over_surf = game.load_picture(os.path.join(IMAGE_PATH, "stash_over.png"), True)
		
		leave_button = ui.ScalableButton(screen, (round(LEAVE_X), round(LEAVE_Y)), exit_up_surf, exit_over_surf, BUTTON_SCALE, "bottomright")
		up1_button = ui.ScalableButton(screen, (round(UP_X), round(UP_Y)), up1_up_surf, up1_over_surf, 6, "topleft")
		up2_button = ui.ScalableButton(screen, (round(UP2_X), round(UP_Y)), up2_up_surf, up2_over_surf, 6, "topleft")
		stash_button = ui.ScalableButton(screen, (round(UP_X), round(171)), stash_surf, stash_over_surf, 6, "topleft")
		energy_button = ui.ScalableButton(screen, (round(43), round(302)), energy_surf, energy_over_surf, 6, "topleft")
		max_hp_button = pygwidgets.TextButton(screen, ((round(174), round(302))), "+MAX HP", fontSize=10)
		
		#up3_button = ui.Button(screen, (round(UP3_X), round(UP_Y)), up1_up_surf, up1_over_surf, 6, "topleft")
		#up4_button = ui.Button(screen, (round(UP4_X), round(UP_Y)), up2_up_surf, up2_over_surf, 6, "topright")
		
		dealer = ui.ScalableDisplay(screen, (775, 25), dealer_surf, 8.5, "topright")
		border1 = ui.ScalableDisplay(screen, (25,25), border1_surf, 1, "topleft")
		border2 = ui.ScalableDisplay(screen, (525,25), border1_surf, 1, "topleft", flip_x= True)
		
		up1_info_text = "Copper Shovel\n--------------------\n+1 Break Damage"
		up2_info_text = "Netherite Shovel\n--------------------\n+2 Break Damage"
		stash_info_text = "BF Bag\n--------------------\n+50 Bag Slot"
		energy_info_text = "Monsta Energy\n--------------------\n+50 Max Energy"
		
		self.up1_info = pygwidgets.DisplayText(screen, (598,250), up1_info_text, os.path.join(FONT_PATH, "Silkscreen-Regular.ttf"), fontSize = 15, width = 177, height = 250 , textColor = "white", backgroundColor = "#252525")
		self.up2_info = pygwidgets.DisplayText(screen, (598,250), up2_info_text, os.path.join(FONT_PATH, "Silkscreen-Regular.ttf"), fontSize = 15, width = 177, height = 250 , textColor = "white", backgroundColor = "#252525")
		self.stash_info = pygwidgets.DisplayText(screen, (598,250), stash_info_text, os.path.join(FONT_PATH, "Silkscreen-Regular.ttf"), fontSize = 15, width = 177, height = 250 , textColor = "white", backgroundColor = "#252525")
		self.energy_info = pygwidgets.DisplayText(screen, (598,250), energy_info_text, os.path.join(FONT_PATH, "Silkscreen-Regular.ttf"), fontSize = 15, width = 177, height = 250 , textColor = "white", backgroundColor = "#252525")
		
		self.shop_group = ui.UIGroup({
			"leave": leave_button,
			"up1": up1_button, 
			"up2": up2_button, 
			"dealer": dealer, 
			"border": border1, 
			"border2": border2, 
			"stash_button": stash_button, 
			"energy_button": energy_button
		})

		self.shop_group2 = ui.PygwidgetsUIGroup({
			"max_hp": max_hp_button
		})

	def run_loop(self):
		super().run_loop()
		events = pygame.event.get()
		
		mouse_pos = pygame.mouse.get_pos()
		clicked = self.shop_group.update(mouse_pos, events)
		clicked2 = self.shop_group2.update(events)
		self.screen.fill("#000000")
		for event in events:
			if event.type == pygame.QUIT:
				self.scene_manager.stop()
				return
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					self.scene_manager.go_back()
					return
		if clicked2["max_hp"] and self.player_stats.buy(5):
			self.player_stats.add_max_health(1)
		
		if clicked["leave"]:
			self.scene_manager.go_back()
			return
		
		if clicked["up1"] and self.player_stats.buy(5):
			self.player_stats.break_damage += 1
		
		if clicked["up2"] and self.player_stats.buy(10):
			self.player_stats.break_damage += 2
	
		if clicked["stash_button"] and self.player_stats.buy(10):
			self.player_stats.max_block += 50
		
		if clicked["energy_button"] and self.player_stats.buy(10):
			self.player_stats.max_energy += 50
		
		self.shop_group.draw()
		self.shop_group2.draw()

		pygame.display.flip()

		self.dt = self.clock.tick(FPS_UI) / 1000
		self.dt = min(self.dt, 1 / FPS_UI)

class BarScene(Scene):
	def __init__(self, screen: pygame.Surface, scene_manager: SceneManager, player_stats: game.PlayerStats):
		super().__init__(screen, scene_manager)
		self.player_stats = player_stats
		
		convert_button = pygwidgets.TextButton(self.screen, (SCREEN_WIDTH - 100, 50), "Convert", textColor="white", fontSize=32)
		add_energy_button = pygwidgets.TextButton(self.screen, (SCREEN_WIDTH - 100, 100), "+Energy", textColor="white", fontSize=32)
		shop_button = pygwidgets.TextButton(self.screen, (SCREEN_WIDTH - 100, 150), "Shop", textColor="white", fontSize=32)
		leave_button = pygwidgets.TextButton(self.screen, (SCREEN_WIDTH - 100, 200), "Leave", textColor="white", fontSize=32)
		add_health_button = pygwidgets.TextButton(self.screen, (SCREEN_WIDTH - 100, 250), "+Health", textColor="white", fontSize=32)
				

		self.bar_group = ui.PygwidgetsUIGroup({
			"convert": convert_button, 
			"add_energy": add_energy_button, 
			"shop": shop_button, 
			"leave": leave_button, 
			"add_health": add_health_button
		})
		
	def run_loop(self):
		super().run_loop()
		events = pygame.event.get()
	
		clicked = self.bar_group.update(events)
		
		self.screen.fill("#000000")
		for event in events:
			if event.type == pygame.QUIT:
				self.scene_manager.stop()
				return
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					self.scene_manager.go_back()
					return
			
		
		if clicked["convert"]:
			self.player_stats.convert_block_to_money()

		if clicked["add_energy"]:
			if self.player_stats.buy(5):
				self.player_stats.refill_energy()

		if clicked["shop"]:
			self.scene_manager.change_scene(SHOP_SCENE_KEY)

		if clicked["leave"]:
			self.scene_manager.go_back()

		if clicked["add_health"]:
			if self.player_stats.buy(5):
				self.player_stats.add_health(1)

		
		self.bar_group.draw()

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

		PLAY_BTN_Y = round(SCREEN_HEIGHT / 1.55)
		EXIT_BTN_Y = round(SCREEN_HEIGHT / 1.325)
		LOGO_Y = round(SCREEN_HEIGHT / 2.85)
		BUTTON_SCALE = SCREEN_WIDTH / SCREEN_HEIGHT * 4 if FULL_SCREEN else 3
		LOGO_SCALE = SCREEN_WIDTH / SCREEN_HEIGHT * 0.55 if FULL_SCREEN else 0.5

		# Main Menu
		play_up_surf = game.load_picture(os.path.join(IMAGE_PATH, "play.png"), True)
		play_over_surf = game.load_picture(os.path.join(IMAGE_PATH, 'play_over.png'), True)
		exit_up_surf = game.load_picture(os.path.join(IMAGE_PATH, "exit.png"), True)
		exit_over_surf = game.load_picture(os.path.join(IMAGE_PATH, "exit_over.png"), True)
		logo_surf = game.load_picture(os.path.join(IMAGE_PATH, "logo.png"), True)
		
		# Main Menu Button
		play_button = ui.ScalableButton(screen, (SCREEN_WIDTH_HALF, PLAY_BTN_Y), play_up_surf, play_over_surf, BUTTON_SCALE)
		exit_button = ui.ScalableButton(screen, (SCREEN_WIDTH_HALF, EXIT_BTN_Y), exit_up_surf, exit_over_surf, BUTTON_SCALE)
		logo = ui.ScalableDisplay(screen, (SCREEN_WIDTH_HALF, LOGO_Y), logo_surf, LOGO_SCALE)
		exit_desktop_button = ui.ScalableButton(screen, (SCREEN_WIDTH_HALF, round(SCREEN_HEIGHT / 1.2)), exit_up_surf, exit_over_surf, BUTTON_SCALE)
			
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
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					self.scene_manager.go_back()
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