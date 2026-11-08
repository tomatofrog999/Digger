import pygame
import sys
import os
import game_essential as game
import game_ui as ui
import pygwidgets
from game_constant import *
from collections.abc import Callable
import math

def main():
	pygame.init()
	pygame.mixer.init()

	screen_info = pygame.display.Info()
	SCREEN_WIDTH = screen_info.current_w if FULL_SCREEN else ORIGINAL_SCREEN_WIDTH
	SCREEN_HEIGHT = screen_info.current_h if FULL_SCREEN else ORIGINAL_SCREEN_HEIGHT
	SCREEN_WIDTH_HALF = SCREEN_WIDTH // 2
	SCREEN_HEIGHT_HALF = SCREEN_HEIGHT // 2
	CAM_Y_UNDERGROUND_OFFSET = SCREEN_HEIGHT // 8

	PLAY_BTN_Y = round(SCREEN_HEIGHT / 1.55)
	EXIT_BTN_Y = round(SCREEN_HEIGHT / 1.325)
	LOGO_Y = round(SCREEN_HEIGHT / 2.85)

	BUTTON_SCALE = SCREEN_WIDTH / SCREEN_HEIGHT * 4 if FULL_SCREEN else 3
	LOGO_SCALE = SCREEN_WIDTH / SCREEN_HEIGHT * 0.55 if FULL_SCREEN else 0.5
	LEAVE_SCALE = SCREEN_WIDTH/SCREEN_HEIGHT * 4 if FULL_SCREEN else 4
	UP_SCALE = 1 if FULL_SCREEN else 6
	DEALER_SCALE = 1 if FULL_SCREEN else 8.5

	screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
	pygame.display.set_caption("Digger Game")
	clock = pygame.time.Clock()

	CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
	BASE_PATH = os.path.dirname(CURRENT_PATH)
	ASSET_PATH = os.path.join(BASE_PATH, "assets")
	IMAGE_PATH = os.path.join(ASSET_PATH, "images")
	MUSIC_PATH = os.path.join(ASSET_PATH, "musics")

	# Main Menu
	play_up_surf = game.load_picture(os.path.join(IMAGE_PATH, "play.png"), True)
	play_over_surf = game.load_picture(os.path.join(IMAGE_PATH, 'play_over.png'), True)
	exit_up_surf = game.load_picture(os.path.join(IMAGE_PATH, "exit.png"), True)
	exit_over_surf = game.load_picture(os.path.join(IMAGE_PATH, "exit_over.png"), True)
	logo_surf = game.load_picture(os.path.join(IMAGE_PATH, "logo.png"), True)

	# Main Menu Button
	play_button = ui.ScalableButton(screen, (SCREEN_WIDTH_HALF, PLAY_BTN_Y), play_up_surf, play_over_surf, BUTTON_SCALE)
	exit_button = ui.ScalableButton(screen, (SCREEN_WIDTH_HALF, EXIT_BTN_Y), exit_up_surf, exit_over_surf, BUTTON_SCALE)
	logo = ui.ScalableButton(screen, (SCREEN_WIDTH_HALF, LOGO_Y), logo_surf, logo_surf, LOGO_SCALE)

	main_menu_group = ui.UIGroup([play_button, exit_button, logo])

	BREAK_EFFECT_SHEET = game.load_picture(os.path.join(IMAGE_PATH, "break_effect.png"), True)
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

	platform_group = pygame.sprite.Group()

	PLATFORM1_SURFACE = pygame.Surface((BLOCK_WIDTH * BLOCK_PER_WIDTH, BLOCK_HEIGHT * BLOCK_PER_HEIGHT))
	PLATFORM1_SURFACE.fill("brown")
	PLATFORM2_SURFACE = PLATFORM1_SURFACE.copy()

	PLATFORM1 = game.PlatformSprite(PLATFORM1_SURFACE, (0, 0))
	PLATFORM1.get_rect().topright = MINE_POS

	PLATFORM2 = game.PlatformSprite(PLATFORM2_SURFACE, (MINE_POS[0] + BLOCK_WIDTH * BLOCK_PER_WIDTH, MINE_POS[1]))

	game_state = game.GameState(MAP1_DATA, WORLD_SEED)
	game_state.create_new_block_group()

	platform_group.add(PLATFORM1)
	platform_group.add(PLATFORM2)

	display_text1 = pygwidgets.DisplayText(screen, (0, 0), "Test", textColor="white", fontSize=32)
	display_text1.setCenteredLoc((SCREEN_WIDTH_HALF, 20))

	display_text2 = pygwidgets.DisplayText(screen, (0, 0), "Test", textColor="white", fontSize=32)
	display_text2.setCenteredLoc((SCREEN_WIDTH_HALF, SCREEN_HEIGHT - 20))

	# Create player and animation
	animation_dict = {
		game.PlayerSprite.AnimationState.IDLE: game.PlayerSprite.AnimationData(0, 4, 150, True, 0),
		game.PlayerSprite.AnimationState.WALK: game.PlayerSprite.AnimationData(4, 6, 120, True, 0),
		game.PlayerSprite.AnimationState.JUMP: game.PlayerSprite.AnimationData(10, 4, 120, False, 3),
		game.PlayerSprite.AnimationState.WALL_JUMP: game.PlayerSprite.AnimationData(10, 4, 100, False, 3),
		game.PlayerSprite.AnimationState.WALL_SLIDE: game.PlayerSprite.AnimationData(5, 1, 200, True, 2),
		game.PlayerSprite.AnimationState.FALL: game.PlayerSprite.AnimationData(11, 3, 150, True, 1),
		game.PlayerSprite.AnimationState.DIG: game.PlayerSprite.AnimationData(17, 3, 100, False, 3)
	}
	player_surface = game.load_picture(os.path.join(IMAGE_PATH, "doux.png"), True)
	player_stats = game.PlayerStats().init_break_damage(START_BREAK_DAMAGE, START_BREAK_DAMAGE_MODIFIER).init_max_block(START_MAX_INVENTORY) \
				.init_max_energy(START_ENERGY).init_max_health(START_HEALTH).init_on_beat_constant(START_ON_BEAT_EXTRA_DMG, START_ON_BEAT_EXTRA_DMG_MODIFIER) \
				.init_rate_of_convertion(START_RATE_OF_CONVERTION)
	player_stats.check_init()
	player = game.PlayerSprite((-200, 0), PLAYER_HITBLOCK_SIZE, player_stats).init_screen(screen).init_image_offset(PLAYER_IMAGE_OFFSET) \
			.init_breakable_group(game_state.get_block_group()).init_animation_data(animation_dict) \
			.init_unbreakable_group(platform_group)
	player.set_surface(player_surface, PLAYER_SURFACE_SIZE, PLAYER_SURFACE_SCALE)
	player.check_init()

	camera = game.Camera(player.get_rect().x, player.get_rect().y).init_dynamic_camera_constant(CAM_Y_UNDERGROUND_OFFSET, CAM_SPEED_SCALE, MINE_POS, CAM_MIN_DISTANCE) \
			.init_cam_offset(SCREEN_WIDTH_HALF, SCREEN_HEIGHT_HALF)
	camera.check_init()

	RHYTHM_BAR_WIDTH = SCREEN_WIDTH * 3 // 4
	rhythm_handler = game.RhythmHandler(os.path.join(MUSIC_PATH, "loudness_log.txt"), RHYTHM_ERROR_MARGIN_MS, RHYTHM_BAR_WIDTH, RHYTHM_BAR_HEIGHT, RHYTHM_SHOW_LENGTH_MS, WRONG_PRESS_COOLDOWN_MS) \
					.init_screen(screen, RHYTHM_BAR_LINE_RATIO, (SCREEN_WIDTH_HALF, SCREEN_HEIGHT - 30))
	rhythm_handler.check_init()

	text_button1 = pygwidgets.TextButton(screen, (SCREEN_WIDTH - 100, 50), "Convert", textColor="white", fontSize=32)
	text_button2 = pygwidgets.TextButton(screen, (SCREEN_WIDTH - 100, 100), "+Energy", textColor="white", fontSize=32)

	text_button3 = pygwidgets.TextButton(screen, (0, 50), "Save", textColor="white", fontSize=32)
	text_button4 = pygwidgets.TextButton(screen, (0, 100), "Load", textColor="white", fontSize=32)
	text_button5 = pygwidgets.TextButton(screen, (0, 150), "Reset", textColor="white", fontSize=32)
	text_button6 = pygwidgets.TextButton(screen, (0, 200), "Random", textColor="white", fontSize=32)

	dt = 0
	tick = 0
	time_passed = 0 # for fps debug
	running = True
	real_dt = 0
	in_menu = True
	in_shop = False
	already_started = False
	while running:
		events = pygame.event.get()
		pressed_dig = False
		clicked1 = False
		clicked2 = False
		clicked3 = False
		clicked4 = False
		clicked5 = False
		clicked6 = False
		for event in events:
			if event.type == pygame.QUIT:
				running = False
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					if in_menu:
						running = False
					else:
						in_menu = True
						rhythm_handler.pause()
				if event.key in (pygame.K_j, pygame.K_k):
					pressed_dig = True
			
			clicked1 = text_button1.handleEvent(event)
			clicked2 = text_button2.handleEvent(event)
			clicked3 = text_button3.handleEvent(event)
			clicked4 = text_button4.handleEvent(event)
			clicked5 = text_button5.handleEvent(event)
			clicked6 = text_button6.handleEvent(event)

		screen.fill("#171722")

		keys = pygame.key.get_pressed()
		mouse_pos = pygame.mouse.get_pos()

		if in_menu:
			main_menu_group.update(mouse_pos, events)
	
			if play_button.clicked:
				in_menu = False
				if not already_started:
					rhythm_handler.start(os.path.join(MUSIC_PATH, r"separated\htdemucs\bad_apple\drums.flac"), 0.7)
					already_started = True
				else:
					rhythm_handler.unpause()
				continue
	
			if exit_button.clicked:
				running = False
		else:
			rhythm_handler.update(player, pressed_dig)

			player.update(keys, events, dt, game_state)

			if player_stats.game_over:
				print("Game Over")
				running = False
			
			# Update camera movement
			player_rect = player.get_rect()
			camera.update(player_rect, dt)

			display_text1.setText(f"Health: {player_stats.health}/{player_stats.max_health} Block: {player_stats.block}/{player_stats.max_block} Energy: {player_stats.energy}/{player_stats.max_energy} Money: {player_stats.money}")
			display_text1.setCenteredLoc((SCREEN_WIDTH_HALF, 20))

			display_text2.setText(f"{game_state.seed}")
			display_text2.setCenteredLoc((SCREEN_WIDTH_HALF, SCREEN_HEIGHT - 100))

			if clicked1:
				player_stats.convert_block_to_money()

			if clicked2:
				player_stats.refill_energy()

			if clicked3:
				game.save_game(AUTO_SAVE_FILE_NAME, player_stats, game_state)

			if clicked4:
				try:
					game.load_game(AUTO_SAVE_FILE_NAME, player_stats, game_state, player)
				except FileNotFoundError as e:
					print(str(e))

			if clicked5:
				game_state.reset_block_broken(player)
				player_stats.reset()

			if clicked6:
				game_state.random_seed()
				game_state.create_new_block_group()
				player.breakable_group = game_state.block_group

				game_state.reset_block_broken(player)
				player_stats.reset()

			# --- DRAWING ---
			cam_offset = camera.get_cam_offset()

			for block in game_state.get_block_group():
				if block.image == None:
					raise TypeError("'image' variable cannot be None type.")
				screen.blit(block.image, (round(block.get_rect().x + cam_offset[0]), round(block.get_rect().y + cam_offset[1])))
				if block.damage_taken > 0:
					break_level = math.floor(block.damage_taken / block.max_health * BREAK_EFFECT_LENGTH)
					temp_surf = game.get_surface_from_sprite_sheet(BREAK_EFFECT_SHEET, (break_level, 0), (BREAK_EFFECT_WIDTH, BREAK_EFFECT_WIDTH), block.get_rect().size[0] / BREAK_EFFECT_WIDTH, True)
					screen.blit(temp_surf, (round(block.get_rect().x + cam_offset[0]), round(block.get_rect().y + cam_offset[1])))

			for platform in platform_group:
				if platform.image == None:
					raise TypeError("'platform' variable cannot be None type.")
				screen.blit(platform.image, (round(platform.get_rect().x + cam_offset[0]), round(platform.get_rect().y + cam_offset[1])))

			player.draw(cam_offset)

			rhythm_handler.draw()

			display_text1.draw()
			display_text2.draw()
			text_button1.draw()
			text_button2.draw()
			text_button3.draw()
			text_button4.draw()
			text_button5.draw()
			text_button6.draw()

		if in_menu:
			main_menu_group.draw()

		pygame.display.flip()


		# --- DEBUG---
		if tick >= TARGET_TICK:
			# print(f"FPS_avg: {(TARGET_TICK) / time_passed if time_passed > 0 else 0:.2f} FPS: {(1 / real_dt) if real_dt > 0 else 0:.2f} at: {player.airtime_tick} twt: {player.touch_wall_tick} ac: {player.action}                ", end="\r")
			tick = 0
			time_passed = 0

		
		tick += 1
		dt = clock.tick(FPS) / 1000
		real_dt = dt
		time_passed += dt
		dt = min(dt, 1 / FPS)

	print("\n\n")
	pygame.quit()
	sys.exit()

class MainScene:
	pass

class Scene:
	def __init__(self, main_loop_func: Callable, start_func: Callable, end_function: Callable):
		self.main_loop_func = main_loop_func
		self.start_func = start_func
		self.end_function = end_function
		self.started = False
		self.running = True

	def start(self):
		if not self.started:
			self.start_func()
			self.started = True

	def run_loop(self):
		if not self.started:
			self.start()
		self.main_loop_func()

	def stop(self):
		self.end_function()
		self.started = False

if __name__ == "__main__":
	main()