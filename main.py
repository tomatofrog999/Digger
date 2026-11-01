import pygame
import pygwidgets
import sys
import random as r
from enum import Enum

class AnimationState(Enum):
	IDLE = 0
	WALK = 1

class TouchWallState(Enum):
	NOT_TOUCH_WALL = 0
	TOUCH_WALL_RIGHT = 1
	TOUCH_WALL_LEFT = 2

class BlockSprite(pygame.sprite.Sprite):
	max_health : float = 0
	damage_taken : float = 0

	def __init__(self, surface : pygame.Surface, topleft : tuple[int, int], max_health : float):
		super().__init__()

		self.image = surface
		
		self.rect : pygame.Rect = self.image.get_rect()
		self.rect.topleft = topleft

		self.max_health = max_health

	def kill(self):
		super().kill()

class PlayerSprite(pygame.sprite.Sprite):
	ANIMATION_IDLE_START_INDEX = 0
	ANIMATION_IDLE_STEP = 4
	ANIMATION_WALK_START_INDEX = 4
	ANIMATION_WALK_STEP = 6
	ANIMATION_COLLDOWN_MS = 150 # ms
	walk_surface : tuple[pygame.Surface, ...] = None
	idle_surface : tuple[pygame.Surface, ...] = None
	time_since_update_animation : int = 0
	animation_frame : int = 0
	last_animation_state : AnimationState = AnimationState.IDLE

	max_health = 3
	health = 3
	max_energy = 100
	energy = 100
	def __init__(self, animation_surface : pygame.Surface, topleft : tuple[int, int], size_per_image : tuple[int, int], surface_scale : int, hitblock_size : tuple[int, int]):
		super().__init__()
		self.set_surface(animation_surface, topleft, size_per_image, surface_scale, hitblock_size)

	def set_surface(self, animation_surface : pygame.Surface, topleft : tuple[int, int], size_per_image : tuple[int, int], surface_scale : int, hitblock_size : tuple[int, int]):
		self.rect : pygame.Rect = pygame.Rect(topleft, hitblock_size)
		self.init_animation(animation_surface, size_per_image, surface_scale)
		self.image = self.get_surface_from_state(AnimationState.IDLE)[0]

	def get_surface_from_state(self, state : AnimationState) -> pygame.Surface:
		if state == AnimationState.IDLE:
			return self.idle_surface
		elif state == AnimationState.WALK:
			return self.walk_surface
		return None
	
	def draw(self, screen : pygame.Surface, topleft : tuple[int, int], facing_left : bool, animation_state : AnimationState):
		current_time = pygame.time.get_ticks()

		if animation_state != self.last_animation_state:
			self.last_animation_state = animation_state
			self.animation_frame = 0
			self.time_since_update_animation = current_time	

		animation = self.get_surface_from_state(animation_state)
		if current_time >= self.time_since_update_animation + PlayerSprite.ANIMATION_COLLDOWN_MS:
			self.time_since_update_animation = current_time
			self.animation_frame = (self.animation_frame + 1) if self.animation_frame + 1 < len(animation) else 0

		surf = animation[self.animation_frame]

		if facing_left:
			surf = pygame.transform.flip(surf, True, False)

		screen.blit(surf, topleft)

	def init_animation(self, animation_surface : pygame.Surface, size_per_image : tuple[int, int], surface_scale : int):
		temp_list = []
		for i in range(PlayerSprite.ANIMATION_IDLE_START_INDEX, PlayerSprite.ANIMATION_IDLE_STEP):
			temp_list.append(self.create_animation_surface(animation_surface, i, size_per_image, surface_scale))
		self.idle_surface = tuple(temp_list)

		temp_list = []
		for i in range(PlayerSprite.ANIMATION_WALK_START_INDEX, PlayerSprite.ANIMATION_WALK_STEP):
			temp_list.append(self.create_animation_surface(animation_surface, i, size_per_image, surface_scale))
		self.walk_surface = tuple(temp_list)


	def create_animation_surface(self, animation_surface : pygame.Surface, animation_number : int, size_per_image : tuple[int, int], scale : int) -> pygame.Surface:
		width, height = size_per_image
		image = pygame.Surface(size_per_image, pygame.SRCALPHA)
		image.blit(animation_surface, (0,0) ,((animation_number * width, 0) ,size_per_image))
		image = pygame.transform.scale(image, (width * scale, height * scale))
		return image

class BlockData:
	surface : pygame.Surface = None
	max_health : float = 1
	spawn_weight : float = 0

	def __init__(self, surface : pygame.Surface, max_health : float, spawn_weight : float):
		self.surface = surface
		self.max_health = max_health
		self.spawn_weight = spawn_weight

class LayerData:
	end_layer : int = 0
	block_tuple : tuple[BlockData, ...] = None
	def __init__(self, end_layer : int, block_tuple : tuple[BlockData, ...]):
		self.end_layer = end_layer
		self.block_tuple = block_tuple
		combined_weight = 0
		for x in self.block_tuple:
			combined_weight += x.spawn_weight

		if round(combined_weight, 4) != 1.0000:
			raise ValueError("Combined weight of BlockData in BlockLayerData != 1")

	def get_random_block(self) -> BlockData:
		temp_random = r.random()
		length = len(self.block_tuple)
		combined_weight = 0
		for i in range(length):
			current_weight = self.block_tuple[i].spawn_weight
			if round(combined_weight + current_weight, 4) > temp_random:
				return self.block_tuple[i]
			combined_weight = round(combined_weight + current_weight, 4)

		if temp_random == 1:
			return self.block_tuple[r.randint(0, length - 1)]

		raise RuntimeError(f"Impossible state")

class MapData:
	layer_tuple : tuple[LayerData, ...] = None
	def __init__(self, layer_tuple : tuple[LayerData, ...]):
		self.layer_tuple = sorted(layer_tuple, key=(lambda x: x.end_layer))

	def create_sprite_group(self, width : int, height : int, map_position : tuple[int, int]) -> pygame.sprite.Group:
		block_group = pygame.sprite.Group()
		block_x, block_y = 0, 0
		layer_index = 0
		layer = self.layer_tuple[layer_index]
		length = len(self.layer_tuple)
		for i in range(height):
			if i >= layer.end_layer:
				layer_index += 1
				if layer_index >= length:
					break
				layer = self.layer_tuple[layer_index]
			block_x = 0
			for j in range(width):
				block_data = layer.get_random_block()
				block = BlockSprite(block_data.surface, (block_x + map_position[0], block_y + map_position[1]), block_data.max_health)
				block_group.add(block)
				block_x += block_data.surface.size[0]
			block_y += block_data.surface.size[1]
		return block_group

	
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

GRAVITY_ACCERELATION = 10.0

BLOCK_WIDTH = 64
BLOCK_PER_WIDTH = 15
BLOCK_PER_HEIGHT = 50
MINE_POS = (-100, 400)

# Layer 1
BLOCK1_SURFACE = pygame.Surface((BLOCK_WIDTH, BLOCK_WIDTH))
BLOCK1_SURFACE.fill("brown3")
BLOCK1_DATA = BlockData(BLOCK1_SURFACE, 3.0, 0.8)

BLOCK2_SURFACE = pygame.Surface((BLOCK_WIDTH, BLOCK_WIDTH))
BLOCK2_SURFACE.fill("chocolate1")
BLOCK2_DATA = BlockData(BLOCK2_SURFACE, 6.0, 0.2)

LAYER1_DATA = LayerData(10, (BLOCK1_DATA, BLOCK2_DATA))


# Layer 2
BLOCK3_SURFACE = pygame.Surface((BLOCK_WIDTH, BLOCK_WIDTH))
BLOCK3_SURFACE.fill("red")
BLOCK3_DATA = BlockData(BLOCK3_SURFACE, 10.0, 0.6)

BLOCK4_SURFACE = pygame.Surface((BLOCK_WIDTH, BLOCK_WIDTH))
BLOCK4_SURFACE.fill("pink")
BLOCK4_DATA = BlockData(BLOCK4_SURFACE, 15.0, 0.4)

LAYER2_DATA = LayerData(25, (BLOCK3_DATA, BLOCK4_DATA))

# Layer 3
BLOCK5_SURFACE = pygame.Surface((BLOCK_WIDTH, BLOCK_WIDTH))
BLOCK5_SURFACE.fill("darkorchid1")
BLOCK5_DATA = BlockData(BLOCK5_SURFACE, 20.0, 0.15)

BLOCK6_SURFACE = pygame.Surface((BLOCK_WIDTH, BLOCK_WIDTH))
BLOCK6_SURFACE.fill("darkmagenta")
BLOCK6_DATA = BlockData(BLOCK6_SURFACE, 35.0, 0.8)

BLOCK7_SURFACE = pygame.Surface((BLOCK_WIDTH, BLOCK_WIDTH))
BLOCK7_SURFACE.fill("plum2")
BLOCK7_DATA = BlockData(BLOCK7_SURFACE, 40.0, 0.05)

LAYER3_DATA = LayerData(50, (BLOCK5_DATA, BLOCK6_DATA, BLOCK7_DATA))


MAP1_DATA = MapData((LAYER1_DATA, LAYER2_DATA, LAYER3_DATA))

PLAYER_WALK_SPEED = 250.0
PLAYER_MAX_SIDE_SPEED = 1200.0
PLAYER_MAX_DOWN_SPEED = 1200.0
PLAYER_MAX_UP_SPEED = 500.0
PLAYER_SLOW_DOWN_SPEED = 100.0
PLAYER_JUMP_SPEED = 400.0
PLAYER_WALL_KICK_SPEED = 1000.0
PLAYER_ADDITION_SPEED_WHEN_BREAK_BLOCK = 50.0
PLAYER_WALL_SLIDE_ACCERELATION = GRAVITY_ACCERELATION + 7
PLAYER_WALL_SLIDE_SPEED_THRESHOLD = 200
PLAYER_HITBLOCK_SIZE = (25, 50)
PLAYER_BREAK_BLOCK_DISTANCE_X = BLOCK_WIDTH // 2 + PLAYER_HITBLOCK_SIZE[0] // 2
PLAYER_BREAK_BLOCK_DISTANCE_Y = BLOCK_WIDTH // 2 + PLAYER_HITBLOCK_SIZE[1] // 2
PLAYER_BREAK_BLOCK_DISTANCE = 2 # block
TICK_TILL_ENABLE_SLIDE = 0.1 * FPS
PLAYER_SURFACE_SIZE = (24, 24)
PLAYER_SURFACE_SCALE = 3
PLAYER_IMAGE_OFFSET = (-24, -15)

CAM_MAX_SPEED = 900.0
CAM_SPEED_SCALE = 4.0 # per distance(pixel)
CAM_MIN_DISTANCE = 10

cam_x, cam_y = 0.0, 0.0

player_break_damage = 1.0 # block damage per sec
player_break_damage_modifier = 1.0

player_velocity_x = 0.0
player_velocity_y = 0.0

# Initialization
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mining Game")
clock = pygame.time.Clock()

# Create Player
# player = PlayerSprite((150, 50, 0), (PLAYER_WIDTH, PLAYER_HEIGHT), (0, 0))
player_surface = pygame.image.load('doux.png').convert_alpha()
player = PlayerSprite(player_surface, (0, 0), PLAYER_SURFACE_SIZE, PLAYER_SURFACE_SCALE, PLAYER_HITBLOCK_SIZE)

# Create block group
block_group = MAP1_DATA.create_sprite_group(BLOCK_PER_WIDTH, BLOCK_PER_HEIGHT, MINE_POS)

print("size:", len(block_group))

facing_left = False

dt = 0
tick = 0
airtime_tick = 0
touch_wall_tick = 0
time_passed = 0 # for fps debug
touch_wall_side = 0 # 0 = not, 1 = touch wall right, 2 = touch wall left
running = True
while running:
	space_pressed = False
	j_pressed = False
	k_pressed = False
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
		elif event.type == pygame.KEYDOWN:
			if event.key == pygame.K_ESCAPE:
				running = False
			if event.key == pygame.K_SPACE:
				space_pressed = True
			if event.key == pygame.K_j:
				j_pressed = True
			if event.key == pygame.K_k:
				k_pressed = True

	screen.fill("black")

	keys = pygame.key.get_pressed()
	mouses = pygame.mouse.get_pressed()
	a_pressed = keys[pygame.K_a]
	d_pressed = keys[pygame.K_d]
	w_pressed = keys[pygame.K_w]
	s_pressed = keys[pygame.K_s]
	
	# Player movement
	if (a_pressed or d_pressed) and not (a_pressed and d_pressed):
		if a_pressed:
			facing_left = True
		if d_pressed:
			facing_left = False
		if a_pressed and player_velocity_x > -PLAYER_WALK_SPEED:
			player_velocity_x -= PLAYER_WALK_SPEED
		if d_pressed and player_velocity_x < PLAYER_WALK_SPEED:
			player_velocity_x += PLAYER_WALK_SPEED
	elif player_velocity_x != 0:
		player_velocity_x -= extract_number_sign(player_velocity_x) * min(abs(player_velocity_x), PLAYER_SLOW_DOWN_SPEED)
	player_velocity_x = clamp(player_velocity_x, -PLAYER_MAX_SIDE_SPEED, PLAYER_MAX_SIDE_SPEED)

	can_wall_sliding = touch_wall_tick >= TICK_TILL_ENABLE_SLIDE and airtime_tick > TICK_TILL_ENABLE_SLIDE
	if space_pressed and (airtime_tick <= 3 or can_wall_sliding):
		if can_wall_sliding and touch_wall_side != TouchWallState.NOT_TOUCH_WALL:
			if touch_wall_side == TouchWallState.TOUCH_WALL_LEFT:
				player_velocity_x += PLAYER_WALL_KICK_SPEED
			else:
				player_velocity_x -= PLAYER_WALL_KICK_SPEED
			touch_wall_tick = 0
		player_velocity_y -= PLAYER_JUMP_SPEED

	if can_wall_sliding and player_velocity_y > PLAYER_WALL_SLIDE_SPEED_THRESHOLD:
		player_velocity_y -= PLAYER_WALL_SLIDE_ACCERELATION

	player_velocity_y += GRAVITY_ACCERELATION
	player_velocity_y = clamp(player_velocity_y, -PLAYER_MAX_UP_SPEED, PLAYER_MAX_DOWN_SPEED)


	# Position update and collision check
	touch_wall_side = TouchWallState.NOT_TOUCH_WALL
	player.rect.x += round(player_velocity_x * dt)
	block : BlockSprite
	for block in block_group:
		if pygame.Rect.colliderect(player.rect , block.rect):
			if player_velocity_x > 0:
				player.rect.right = block.rect.left
				touch_wall_side = TouchWallState.TOUCH_WALL_RIGHT
			else:
				player.rect.left = block.rect.right
				touch_wall_side = TouchWallState.TOUCH_WALL_LEFT
			player_velocity_x = 0
			break
	if touch_wall_side == TouchWallState.NOT_TOUCH_WALL:
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
	if (j_pressed or k_pressed) and not ((w_pressed or s_pressed) and (a_pressed or d_pressed)):
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
					block.damage_taken += player_break_damage * player_break_damage_modifier
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
	addition_height = CAM_Y_UNDERGROUND_OFFSET if player.rect.bottom > MINE_POS[1] else -CAM_Y_UNDERGROUND_OFFSET
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

	"""
	# HITBLOCK RENDER TEST
	# temporary for check only
	temp = pygame.Surface(player.rect.size)
	temp.fill((0, 150, 0))
	temp_x , temp_y = player.rect.topleft

	screen.blit(temp, (round(temp_x + cam_offset_x), round(temp_y + cam_offset_y)))
	"""
	if player_velocity_x != 0:
		action = AnimationState.WALK
	else:
		action = AnimationState.IDLE
	player.draw(screen, (round(player.rect.x + cam_offset_x + PLAYER_IMAGE_OFFSET[0]), round(player.rect.y + cam_offset_y + PLAYER_IMAGE_OFFSET[1])), facing_left, action)
	pygame.display.flip()


	# Debug
	if tick >= TARGET_TICK:
		print(f"FPS: {(TARGET_TICK) / time_passed if time_passed > 0 else 0:.2f} pos: {player.rect.topleft} vel: {player_velocity_x, player_velocity_y} at: {airtime_tick} twt: {touch_wall_tick} tws: {touch_wall_side}                 ", end="\r")
		tick = 0
		time_passed = 0

	
	tick += 1
	dt = clock.tick(FPS) / 1000
	time_passed += dt

print("\n\n")
pygame.quit()
sys.exit()
