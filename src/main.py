import pygame
import sys
import math
import os
import game_essential as game
import game_ui as ui
from collections.abc import Callable

# --- CONSTANT ---
FULL_SCREEN = False
ORIGINAL_SCREEN_WIDTH = 800
ORIGINAL_SCREEN_HEIGHT = 600

FPS = 120
FPS_UI = 20
TARGET_TICK = FPS // 4

BLOCK_PER_WIDTH = 15
BLOCK_PER_HEIGHT = 50
MINE_POS = (-100, 400)

BLOCK_WIDTH = 70
BLOCK_HEIGHT = 70

GRAVITY_ACCELERATION = 640

PLAYER_WALK_ACCELERATION = 500.0
PLAYER_MAX_WALK_SPEED = 300.0
PLAYER_MAX_SIDE_SPEED = 1200.0
PLAYER_MAX_DOWN_SPEED = 1200.0
PLAYER_MAX_UP_SPEED = 500.0
PLAYER_SLOW_DOWN_ACCELERATION = 400.0
# # v^2 = u^2 + 2as u = sqrt(2as)
# can jump up 2 block 
# s = block height * 2
PLAYER_JUMP_SPEED = math.sqrt(2 * GRAVITY_ACCELERATION * ((BLOCK_HEIGHT + 5) * 2))
PLAYER_WALL_KICK_SPEED = 150.0
PLAYER_ADDITION_SPEED_WHEN_BREAK_BLOCK = 200.0
PLAYER_WALL_SLIDE_ACCELERATION = GRAVITY_ACCELERATION * 3 / 2
PLAYER_WALL_SLIDE_SPEED_THRESHOLD = 100.0

PLAYER_BREAK_BLOCK_DISTANCE = 3 # block
PLAYER_TICK_TILL_ENABLE_SLIDE = round(0.1 * FPS)

PLAYER_HITBLOCK_SIZE = (25, 50)
PLAYER_SURFACE_SIZE = (24, 24)
PLAYER_SURFACE_SCALE = 3
PLAYER_IMAGE_OFFSET = (-24, -15)

CAM_SPEED_SCALE = 4.0 # add up this much per distance(pixel)
CAM_MIN_DISTANCE = 10.0

RHYTHM_ERROR_MARGIN_MS = 50
WRONG_PRESS_COOLDOWN_MS = 500
RHYTHM_SHOW_LENGTH_MS = 1500 # how much rhythm backward to forward in ms to show on screen

BUTTON_SCALE = 4

def main():
	pygame.init()
	pygame.mixer.init()

	screen_info = pygame.display.Info()
	SCREEN_WIDTH = screen_info.current_w if FULL_SCREEN else ORIGINAL_SCREEN_WIDTH
	SCREEN_HEIGHT = screen_info.current_h if FULL_SCREEN else ORIGINAL_SCREEN_HEIGHT
	SCREEN_WIDTH_HALF = SCREEN_WIDTH // 2
	SCREEN_HEIGHT_HALF = SCREEN_HEIGHT // 2
	CAM_Y_UNDERGROUND_OFFSET = SCREEN_HEIGHT // 8

	BTN_CENTER_X = round(SCREEN_WIDTH / 2)
	PLAY_BTN_Y = round(SCREEN_HEIGHT / 1.55)
	EXIT_BTN_Y = round(SCREEN_HEIGHT / 1.325)

	screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
	pygame.display.set_caption("Digger Game")
	clock = pygame.time.Clock()

	CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
	BASE_PATH = os.path.dirname(CURRENT_PATH)
	ASSET_PATH = os.path.join(BASE_PATH, "assets")
	IMAGE_PATH = os.path.join(ASSET_PATH, "images")
	MUSIC_PATH = os.path.join(ASSET_PATH, "musics")

	play_up_surf = game.load_picture(os.path.join(IMAGE_PATH, "play.png"), True)
	play_over_surf = game.load_picture(os.path.join(IMAGE_PATH, 'play_over.png'), True)
	exit_up_surf = game.load_picture(os.path.join(IMAGE_PATH, "exit.png"), True)
	exit_over_surf = game.load_picture(os.path.join(IMAGE_PATH, "exit_over.png"), True)

	play_button = ui.Button(screen, (round(BTN_CENTER_X), round(PLAY_BTN_Y)), play_up_surf, play_over_surf, BUTTON_SCALE)
	exit_button = ui.Button(screen, (round(BTN_CENTER_X), round(EXIT_BTN_Y)), exit_up_surf, exit_over_surf, BUTTON_SCALE)

	# Layer Constant
	SPRITE_SHEET_SURFACE = game.load_picture(os.path.join(IMAGE_PATH, "tiles_spritesheet.png"), True)
	# Layer 1
	BLOCK1_SURFACE_DATA = game.get_spritesheet_data(os.path.join(IMAGE_PATH, "tiles_spritesheet.txt"), "grassCenter")
	BLOCK1_SURFACE = game.get_surface_from_sprite_sheet2(SPRITE_SHEET_SURFACE, BLOCK1_SURFACE_DATA[0], BLOCK1_SURFACE_DATA[1], 1, False)
	BLOCK1_DATA = game.BlockData(BLOCK1_SURFACE, 3.0, 0.8)

	BLOCK2_SURFACE_DATA = game.get_spritesheet_data(os.path.join(IMAGE_PATH, "tiles_spritesheet.txt"), "stoneCenter")
	BLOCK2_SURFACE = game.get_surface_from_sprite_sheet2(SPRITE_SHEET_SURFACE, BLOCK2_SURFACE_DATA[0], BLOCK2_SURFACE_DATA[1], 1, False)
	BLOCK2_DATA = game.BlockData(BLOCK2_SURFACE, 6.0, 0.2)

	LAYER1_DATA = game.LayerData(10, (BLOCK1_DATA, BLOCK2_DATA), 0.05, 1)


	# Layer 2
	BLOCK3_SURFACE = pygame.Surface((BLOCK_WIDTH, BLOCK_HEIGHT))
	BLOCK3_SURFACE.fill("orange")
	BLOCK3_DATA = game.BlockData(BLOCK3_SURFACE, 10.0, 0.6)

	BLOCK4_SURFACE = pygame.Surface((BLOCK_WIDTH, BLOCK_HEIGHT))
	BLOCK4_SURFACE.fill("pink")
	BLOCK4_DATA = game.BlockData(BLOCK4_SURFACE, 15.0, 0.4)

	LAYER2_DATA = game.LayerData(25, (BLOCK3_DATA, BLOCK4_DATA), 0.05, 3)

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

	LAYER3_DATA = game.LayerData(50, (BLOCK5_DATA, BLOCK6_DATA, BLOCK7_DATA), 0.1, 3)


	MAP1_DATA = game.MapData((LAYER1_DATA, LAYER2_DATA, LAYER3_DATA), BLOCK_WIDTH, BLOCK_HEIGHT)


	# Create block group
	block_group = MAP1_DATA.create_sprite_group(BLOCK_PER_WIDTH, BLOCK_PER_HEIGHT, MINE_POS)

	# Create player and animation
	animation_dict = {
		game.Player.AnimationState.IDLE: game.Player.AnimationData(0, 4, 150, True, 0),
		game.Player.AnimationState.WALK: game.Player.AnimationData(4, 6, 120, True, 0),
		game.Player.AnimationState.JUMP: game.Player.AnimationData(10, 4, 120, False, 3),
		game.Player.AnimationState.WALL_JUMP: game.Player.AnimationData(10, 4, 100, False, 3),
		game.Player.AnimationState.WALL_SLIDE: game.Player.AnimationData(5, 1, 200, True, 2),
		game.Player.AnimationState.FALL: game.Player.AnimationData(11, 3, 150, True, 1),
		game.Player.AnimationState.DIG: game.Player.AnimationData(17, 3, 100, False, 3)
	}
	player_surface = game.load_picture(os.path.join(IMAGE_PATH, "doux.png"), True)
	player = game.Player((0, 0), PLAYER_HITBLOCK_SIZE).init_screen(screen).init_image_offset(PLAYER_IMAGE_OFFSET) \
			.init_breakable_group(block_group).init_energy(100).init_health(3).init_animation_data(animation_dict) \
			.init_walk_constant(PLAYER_WALK_ACCELERATION, PLAYER_SLOW_DOWN_ACCELERATION, PLAYER_MAX_WALK_SPEED) \
			.init_max_speed_constant(PLAYER_MAX_SIDE_SPEED, PLAYER_MAX_DOWN_SPEED, PLAYER_MAX_UP_SPEED) \
			.init_jump_slide_constant(PLAYER_JUMP_SPEED, PLAYER_WALL_KICK_SPEED, PLAYER_WALL_SLIDE_ACCELERATION, PLAYER_WALL_SLIDE_SPEED_THRESHOLD, PLAYER_TICK_TILL_ENABLE_SLIDE) \
			.init_digging_constant(PLAYER_BREAK_BLOCK_DISTANCE, PLAYER_ADDITION_SPEED_WHEN_BREAK_BLOCK, BLOCK_WIDTH, BLOCK_HEIGHT) \
			.init_gravity_constant(GRAVITY_ACCELERATION).init_break_damage_constant(1.0, 1.0).init_on_beat_constant(5.0, 4.0)
	player.set_surface(player_surface, PLAYER_SURFACE_SIZE, PLAYER_SURFACE_SCALE)
	player.check_init()

	camera = game.Camera(0, 0).init_dynamic_camera_constant(CAM_Y_UNDERGROUND_OFFSET, CAM_SPEED_SCALE, MINE_POS, CAM_MIN_DISTANCE) \
			.init_cam_offset(SCREEN_WIDTH_HALF, SCREEN_HEIGHT_HALF)
	camera.check_init()

	rhythm_handler = game.RhythmHandler(os.path.join(MUSIC_PATH, "loudness_log.txt"), RHYTHM_ERROR_MARGIN_MS, SCREEN_WIDTH * 3 // 4, 40, RHYTHM_SHOW_LENGTH_MS, WRONG_PRESS_COOLDOWN_MS) \
					.init_music(os.path.join(MUSIC_PATH, r"separated\htdemucs\bad_apple\drums.flac"), 0.7) \
					.init_screen(screen, 0.3, (SCREEN_WIDTH_HALF, SCREEN_HEIGHT - 30))
	rhythm_handler.check_init()
	rhythm_handler.start()

	dt = 0
	tick = 0
	time_passed = 0 # for fps debug
	running = True
	real_dt = 0
	while running:
		events = pygame.event.get()
		pressed_dig = False
		for event in events:
			if event.type == pygame.QUIT:
				running = False
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					running = False
				if event.key in (pygame.K_j, pygame.K_k):
					pressed_dig = True

		screen.fill("black")

		keys = pygame.key.get_pressed()
		mouse_pos = pygame.mouse.get_pos()

		play_button.update(mouse_pos, events)
		exit_button.update(mouse_pos, events)

		if play_button.clicked:
			print("play clicked")

		if exit_button.clicked:
			print("exit clicked")

		rhythm_handler.update(player, pressed_dig)

		player.update(keys, events, dt)

		if player.game_over:
			print("Game Over")
			running = False
		
		# Update camera movement
		player_rect = player.get_rect()
		camera.update(player_rect, dt)

		# --- DRAWING ---
		cam_offset = camera.get_cam_offset()

		for block in block_group:
			if block.image == None:
				raise TypeError("'image' variable cannot be None type.")
			screen.blit(block.image, (round(block.get_rect().x + cam_offset[0]), round(block.get_rect().y + cam_offset[1])))

		player.draw(cam_offset)

		rhythm_handler.draw()

		play_button.draw()
		exit_button.draw()

		pygame.display.flip()


		# --- DEBUG---
		if tick >= TARGET_TICK:
			print(f"FPS_avg: {(TARGET_TICK) / time_passed if time_passed > 0 else 0:.2f} FPS: {(1 / real_dt) if real_dt > 0 else 0:.2f} at: {player.airtime_tick} twt: {player.touch_wall_tick} ac: {player.action}                ", end="\r")
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
		
class Runnable:
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