import pygame
import sys
import random as r

class BlockSprite(pygame.sprite.Sprite):
	max_health : float = 0
	damage_taken : float = 0
	def __init__(self, surface : pygame.Surface, position : tuple[int, int], max_health : float):
		super().__init__()

		self.image = surface
		
		self.rect : pygame.Rect = self.image.get_rect()
		self.rect.topleft = position

		self.max_health = max_health

class PlayerSprite(pygame.sprite.Sprite):
	def __init__(self, surface : pygame.Surface, position : tuple[int, int]):
		super().__init__()
		
		self.image = surface
		
		self.rect : pygame.Rect = self.image.get_rect()
		self.rect.topleft = position

class BlockData:
	surface : pygame.Surface = None
	max_health : float = 1
	spawn_weight : float = 0

	def __init__(self, surface : pygame.Surface, max_health : float, spawn_weight : float):
		self.surface = surface
		self.max_health = max_health
		self.spawn_weight = spawn_weight

class BlockLayerData:
	end_layer : int = None
	blocks_data : tuple[BlockData, ...] = None
	def __init__(self, end_layer : int, blocks_data : tuple[BlockData, ...]):
		self.end_layer = end_layer
		self.blocks_data = blocks_data

def clamp(val : int | float, min_val : int | float, max_val : int | float) -> int | float:
	return min(max(val, min_val), max_val)

def extract_number_sign(value : int | float):
	if value == 0: 
		return 0
	return 1 if value > 0 else -1

def in_range(value : int | float, min_val : int | float, max_val : int | float) -> bool:
	return (min_val < value < max_val)

pygame.init()

# Constant
FULL_SCREEN = False
screen_info = pygame.display.Info()
WIDTH = screen_info.current_w if FULL_SCREEN else 800
HEIGHT = screen_info.current_h if FULL_SCREEN else 600
WIDTH_HALFED = WIDTH // 2
HEIGHT_HALFED = HEIGHT // 2
CAM_Y_UNDERGROUND_OFFSET = HEIGHT // 8
FPS = 60
TARGET_TICK = FPS // 4

GRAVITY_SPEED = 10.0

BLOCK_WIDTH = 64
BLOCK1_HEALTH = 5.0
BLOCK2_HEALTH = 10.0
BLOCK1_SURFACE = pygame.Surface((BLOCK_WIDTH, BLOCK_WIDTH))
BLOCK2_SURFACE = BLOCK1_SURFACE.copy()
BLOCK1_SURFACE.fill("green")
BLOCK2_SURFACE.fill("orange")
BLOCK1_DATA = BlockData(BLOCK1_SURFACE, BLOCK1_HEALTH, 0.8)
BLOCK2_DATA = BlockData(BLOCK2_SURFACE, BLOCK2_HEALTH, 0.2)
LAYER1_DATA = BlockLayerData(0, (BLOCK1_DATA, BLOCK2_DATA))
MAP1_LAYER_DATA = (LAYER1_DATA)

MINE_POS_X, MINE_POS_Y = -100, 400

BLOCK_PER_WIDTH = 15
BLOCK_PER_HEIGHT = 50

PLAYER_SPEED = 50.0
PLAYER_MAX_WALK_SPEED = 250.0
PLAYER_MAX_SIDE_SPEED = 1200.0
PLAYER_MAX_DOWN_SPEED = 1200.0
PLAYER_MAX_UP_SPEED = 500.0
PLAYER_SLOW_DOWN_SPEED = 100.0
PLAYER_JUMP_SPEED = 400.0
PLAYER_WALL_KICK_SPEED = 600.0
PLAYER_ADDITION_SPEED_WHEN_BREAK_BLOCK = 200.0
PLAYER_WALL_SLIDE_SPEED = GRAVITY_SPEED + 7
PLAYER_WALL_SLIDE_SPEED_THRESHOLD = 200
PLAYER_WIDTH = 25
PLAYER_HEIGHT = 50
PLAYER_BREAK_BLOCK_DISTANCE_X = BLOCK_WIDTH // 2 + PLAYER_WIDTH // 2
PLAYER_BREAK_BLOCK_DISTANCE_Y = BLOCK_WIDTH // 2 + PLAYER_HEIGHT // 2
PLAYER_BREAK_BLOCK_DISTANCE = 2 # block
TICK_TILL_ENABLE_SLIDE = 0.2 * FPS

CAM_MAX_SPEED = 900.0
CAM_SPEED_SCALE = 4.0 # per distance(pixel)
CAM_MIN_DISTANCE = 10

NOT_TOUCH_WALL = 0
TOUCH_WALL_RIGHT = 1
TOUCH_WALL_LEFT = 2

# Initialization
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mining Game")
clock = pygame.time.Clock()

cam_x, cam_y = 0.0, 0.0

# Create Player
# player = PlayerSprite((150, 50, 0), (PLAYER_WIDTH, PLAYER_HEIGHT), (0, 0))
player_surface = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT))
player_surface.fill((150, 50, 0))
player = PlayerSprite(player_surface, (0, 0))

player_break_damage = 100.0 # block damage per sec
player_break_damage_modifier = 1.0

player_velocity_x = 0.0
player_velocity_y = 0.0

# Create block group
block_group = pygame.sprite.Group()
block_x, block_y = 0, 0
for i in range(BLOCK_PER_WIDTH):
	for j in range(BLOCK_PER_HEIGHT):
		random_number = r.randint(0, 100)
		block = None
		if random_number > 20:
			block = BlockSprite(LAYER1_DATA.blocks_data[0].surface, (block_x + MINE_POS_X, block_y + MINE_POS_Y), LAYER1_DATA.blocks_data[0].max_health)
		else:
			block = BlockSprite(LAYER1_DATA.blocks_data[1].surface, (block_x + MINE_POS_X, block_y + MINE_POS_Y), LAYER1_DATA.blocks_data[1].max_health)
		block_group.add(block)
		block_y += BLOCK_WIDTH
	block_x += BLOCK_WIDTH
	block_y = 0
	
print("size:", len(block_group))

dt = 0
tick = 0
airtime_tick = 0
touch_wall_tick = 0
time_passed = 0
touch_wall_side = 0 # 0 = not, 1 = touch wall right, 2 = touch wall left
running = True
while running:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
		elif event.type == pygame.KEYDOWN:
			if event.key == pygame.K_ESCAPE:
				running = False

	screen.fill("black")

	keys = pygame.key.get_pressed()
	mouses = pygame.mouse.get_pressed()
	a_pressed = keys[pygame.K_a]
	d_pressed = keys[pygame.K_d]
	w_pressed = keys[pygame.K_w]
	s_pressed = keys[pygame.K_s]
	# Player movement
	if (a_pressed or d_pressed) and not (a_pressed and d_pressed):
		if a_pressed and player_velocity_x > -PLAYER_MAX_WALK_SPEED:
			player_velocity_x -= PLAYER_SPEED
		if d_pressed and player_velocity_x < PLAYER_MAX_WALK_SPEED:
			player_velocity_x += PLAYER_SPEED
	elif player_velocity_x != 0:
		player_velocity_x -= extract_number_sign(player_velocity_x) * min(abs(player_velocity_x), PLAYER_SLOW_DOWN_SPEED)
	player_velocity_x = clamp(player_velocity_x, -PLAYER_MAX_SIDE_SPEED, PLAYER_MAX_SIDE_SPEED)

	can_wall_sliding = touch_wall_tick >= TICK_TILL_ENABLE_SLIDE and airtime_tick > TICK_TILL_ENABLE_SLIDE
	if keys[pygame.K_SPACE] and (airtime_tick <= 0 or can_wall_sliding):
		if can_wall_sliding and touch_wall_side != NOT_TOUCH_WALL:
			if touch_wall_side == TOUCH_WALL_LEFT:
				player_velocity_x += PLAYER_WALL_KICK_SPEED
			else:
				player_velocity_x -= PLAYER_WALL_KICK_SPEED
			touch_wall_tick = 0
		player_velocity_y -= PLAYER_JUMP_SPEED

	if can_wall_sliding and player_velocity_y > PLAYER_WALL_SLIDE_SPEED_THRESHOLD:
		player_velocity_y -= PLAYER_WALL_SLIDE_SPEED

	player_velocity_y += GRAVITY_SPEED
	player_velocity_y = clamp(player_velocity_y, -PLAYER_MAX_UP_SPEED, PLAYER_MAX_DOWN_SPEED)


	# Position update and collision check
	touch_wall_side = NOT_TOUCH_WALL
	player.rect.x += round(player_velocity_x * dt)
	block : BlockSprite
	for block in block_group:
		if pygame.Rect.colliderect(player.rect , block.rect):
			if player_velocity_x > 0:
				player.rect.right = block.rect.left
				touch_wall_side = TOUCH_WALL_RIGHT
			else:
				player.rect.left = block.rect.right
				touch_wall_side = TOUCH_WALL_LEFT
			player_velocity_x = 0
			break
	if touch_wall_side == NOT_TOUCH_WALL:
		touch_wall_tick = 0
	else:
		touch_wall_tick += 1

	touch_ground = False
	player.rect.y += round(player_velocity_y * dt)
	for block in block_group:
		if pygame.Rect.colliderect(player.rect , block.rect):
			if player_velocity_y > 0:
				player.rect.bottom = block.rect.top
				touch_ground = True
			else:
				player.rect.top = block.rect.bottom
			player_velocity_y = 0
			break
	if touch_ground:
		airtime_tick = 0
	else:
		airtime_tick += 1

	# Break block
	if (keys[pygame.K_j] or keys[pygame.K_k]) and not ((w_pressed or s_pressed) and (a_pressed or d_pressed)):
		digging_offset_x = 0
		digging_offset_y = 0
		if w_pressed or s_pressed or a_pressed or d_pressed:
			if w_pressed:
				digging_offset_y -= PLAYER_BREAK_BLOCK_DISTANCE_Y
			if s_pressed:
				digging_offset_y += PLAYER_BREAK_BLOCK_DISTANCE_Y
		
			if a_pressed:
				digging_offset_x -= PLAYER_BREAK_BLOCK_DISTANCE_X
			if d_pressed:
				digging_offset_x += PLAYER_BREAK_BLOCK_DISTANCE_X

		is_collide = False
		for _ in range(PLAYER_BREAK_BLOCK_DISTANCE):
			for block in block_group:
				is_collide = block.rect.collidepoint((player.rect.x + digging_offset_x, player.rect.y + digging_offset_y))
				if is_collide:
					block.damage_taken += player_break_damage * player_break_damage_modifier * dt
					if block.damage_taken >= block.max_health:
						if digging_offset_x != 0:
							player_velocity_x += extract_number_sign(digging_offset_x) * PLAYER_ADDITION_SPEED_WHEN_BREAK_BLOCK
						if digging_offset_y > 0:
							player_velocity_y += PLAYER_ADDITION_SPEED_WHEN_BREAK_BLOCK
						block.kill()
					break
			if is_collide:
				break
			if digging_offset_x != 0 and digging_offset_y == 0:
				digging_offset_x += extract_number_sign(digging_offset_x) * BLOCK_WIDTH
			elif digging_offset_y != 0 and digging_offset_x == 0:
				digging_offset_y += extract_number_sign(digging_offset_y) * BLOCK_WIDTH
					
	# Camera Movement
	cam_displacement_x = player.rect.x - cam_x
	addition_height = CAM_Y_UNDERGROUND_OFFSET if player.rect.bottom >= MINE_POS_Y else 0
	cam_displacement_y = (player.rect.y + addition_height) - cam_y
	cam_distance_x = abs(cam_displacement_x)
	cam_distance_y = abs(cam_displacement_y)
	if cam_displacement_x > CAM_MIN_DISTANCE:
		cam_x += min(cam_distance_x, CAM_SPEED_SCALE * cam_distance_x * dt)
	elif cam_displacement_x < -CAM_MIN_DISTANCE:
		cam_x -= min(cam_distance_x, CAM_SPEED_SCALE * cam_distance_x * dt)
	
	if cam_displacement_y > CAM_MIN_DISTANCE:
		cam_y += min(cam_distance_y, CAM_SPEED_SCALE * cam_distance_y * dt)
	elif cam_displacement_y < -CAM_MIN_DISTANCE:
		cam_y -= min(cam_distance_y, CAM_SPEED_SCALE * cam_distance_y * dt)
	

	# Drawing
	cam_offset_x = -cam_x + WIDTH_HALFED
	cam_offset_y = -cam_y + HEIGHT_HALFED
	for block in block_group:
		screen.blit(block.image, (round(block.rect.x + cam_offset_x), round(block.rect.y + cam_offset_y)))
	
	screen.blit(player.image, (round(player.rect.x + cam_offset_x), round(player.rect.y + cam_offset_y)))

	pygame.display.flip()


	# Debug
	if tick >= TARGET_TICK:
		print(f"FPS: {(TARGET_TICK) / time_passed if time_passed > 0 else 0:.2f} pos: {player.rect.topleft} vel: {player_velocity_x, player_velocity_y} at: {airtime_tick} twt: {touch_wall_tick} tws: {touch_wall_side}         ", end="\r")
		tick = 0
		time_passed = 0

	
	tick += 1
	dt = clock.tick(FPS) / 1000
	time_passed += dt

print("\n\n")
pygame.quit()
sys.exit()
