import pygame
import sys
import random as r

def clamp(val, min_val, max_val):
	return min(max(val, min_val), max_val)

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

GRAVITY_SPEED = 10
MAX_DOWN_SPEED = 1000
MAX_UP_SPEED = 500

BLOCK_WIDTH = 64
BLOCK1_BREAK_TIME = 0.2 * FPS # in tick
BLOCK2_BREAK_TIME = 0.5 * FPS

MINE_POS_X, MINE_POS_Y = -100, 400

BLOCK_PER_WIDTH = 15
BLOCK_PER_HEIGHT = 50

PLAYER_SPEED = 250.0
PLAYER_JUMP_SPEED = 400.0
PLAYER_WALL_KICK_SPEED = 600.0
PLAYER_WALL_KICK_VELOCITY_APPLIED_TICK = 0.2 * FPS
PLAYER_WALL_SLIDE_SPEED = GRAVITY_SPEED + 7
PLAYER_WALL_SLIDE_SPEED_THRESHOLD = 200
PLAYER_WIDTH = 25
PLAYER_HEIGHT = 50
PLAYER_BREAK_BLOCK_DISTANCE_X = 2 * BLOCK_WIDTH + PLAYER_WIDTH // 2
PLAYER_BREAK_BLOCK_DISTANCE_Y = 2 * BLOCK_WIDTH + PLAYER_HEIGHT // 2
TICK_TILL_ENABLE_SLIDE = 0.2 * FPS

CAM_MAX_SPEED = 900.0
CAM_SPEED_SCALE = 4.0 # per distance(pixel)
CAM_MIN_DISTANCE = 0

class BlockSprite(pygame.sprite.Sprite):
	tick_till_break = 1
	current_break_tick = 0.0
	def __init__(self, color, size, pos, break_time):
		super().__init__()
		
		self.image = pygame.Surface(size)
		self.image.fill(color)
		
		self.rect = self.image.get_rect()
		self.rect.center = pos

		self.tick_till_break = break_time

class PlayerSprite(pygame.sprite.Sprite):
	def __init__(self, color, size, pos):
		super().__init__()
		
		self.image = pygame.Surface(size)
		self.image.fill(color)
		
		self.rect = self.image.get_rect()
		self.rect.center = pos

# Initialization
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mining Game")
clock = pygame.time.Clock()

cam_x, cam_y = 0, 0
mouse_x, mouse_y = 0, 0

# Create Player
player = PlayerSprite((150, 50, 0), (PLAYER_WIDTH, PLAYER_HEIGHT), (0, 0))

player_break_speed = 1
player_break_speed_modifier = 1

player_velocity_x = 0
addition_velocity_x = 0
player_velocity_y = 0

# Create block group
block_group = pygame.sprite.Group()
block_x, block_y = 0, 0
for i in range(BLOCK_PER_WIDTH):
	for j in range(BLOCK_PER_HEIGHT):
		block = BlockSprite((0, r.randint(0,255), r.randint(0,255)), (BLOCK_WIDTH, BLOCK_WIDTH), (round(block_x + MINE_POS_X), round(block_y + MINE_POS_Y)), BLOCK1_BREAK_TIME)
		block_group.add(block)
		block_y += BLOCK_WIDTH
	block_x += BLOCK_WIDTH
	block_y = 0
print("size:", len(block_group))

dt = 0
tick = 0
airtime_tick = 0
touch_wall_tick = 0
applied_addition_velocity_tick = 0
time_passed = 0
touch_wall_side = 0 # 0 = not, 1 = touch wall right, 2 = touch wall left
running = True
while running:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
		elif event.type == pygame.MOUSEMOTION:
			mouse_x, mouse_y = event.pos
		elif event.type == pygame.KEYDOWN:
			if event.key == pygame.K_ESCAPE:
				running = False

	screen.fill("black")

	keys = pygame.key.get_pressed()
	mouses = pygame.mouse.get_pressed()

	# Player movement
	if applied_addition_velocity_tick <= 0:
		addition_velocity_x = 0
	else:
		applied_addition_velocity_tick -= 1

	if keys[pygame.K_a]:
		player_velocity_x = -PLAYER_SPEED

	if keys[pygame.K_d]:
		player_velocity_x = PLAYER_SPEED

	if not (keys[pygame.K_a] or keys[pygame.K_d] or keys[pygame.K_RIGHT]):
		player_velocity_x = 0

	can_wall_sliding = touch_wall_tick >= TICK_TILL_ENABLE_SLIDE and airtime_tick > TICK_TILL_ENABLE_SLIDE
	if (keys[pygame.K_w] or keys[pygame.K_SPACE]) and (airtime_tick <= 0 or can_wall_sliding):
		if can_wall_sliding and touch_wall_side != 0:
			if touch_wall_side == 1:
				# touch wall side left kick right
				addition_velocity_x = -PLAYER_WALL_KICK_SPEED
			else:
				# touch wall side right kick left
				addition_velocity_x = PLAYER_WALL_KICK_SPEED
			touch_wall_tick = 0
			applied_addition_velocity_tick = PLAYER_WALL_KICK_VELOCITY_APPLIED_TICK
		player_velocity_y -= PLAYER_JUMP_SPEED

	if can_wall_sliding and player_velocity_y > PLAYER_WALL_SLIDE_SPEED_THRESHOLD:
		player_velocity_y -= PLAYER_WALL_SLIDE_SPEED
	player_velocity_y += GRAVITY_SPEED
	player_velocity_y = clamp(player_velocity_y, -MAX_UP_SPEED, MAX_DOWN_SPEED)


	# Position update and collision check
	touch_wall_side = 0
	touch_wall = False
	combined_velocity_x = (player_velocity_x + addition_velocity_x)
	player.rect.x += combined_velocity_x * dt
	for block in block_group:
		is_collide = pygame.Rect.colliderect(player.rect , block.rect)
		touch_wall = is_collide if not touch_wall else True # if it already true, will not change state again
		if is_collide:
			if combined_velocity_x > 0:
				player.rect.right = block.rect.left
				touch_wall_side = 1
			elif combined_velocity_x < 0:
				player.rect.left = block.rect.right
				touch_wall_side = 2
			player_velocity_x = 0
	if not touch_wall:
		touch_wall_tick = 0
	else:
		touch_wall_tick += 1

	touch_ground = False
	player.rect.y += player_velocity_y * dt
	for block in block_group:
		is_collide = pygame.Rect.colliderect(player.rect , block.rect)
		if is_collide:
			if player_velocity_y > 0:
				player.rect.bottom = block.rect.top
				touch_ground = is_collide if not touch_ground else True
			elif player_velocity_y < 0:
				player.rect.top = block.rect.bottom
			player_velocity_y = 0
	if not touch_ground:
		airtime_tick += 1
	else:
		airtime_tick = 0

	# Break block
	cam_offset_x = -cam_x + WIDTH_HALFED
	cam_offset_y = -cam_y + HEIGHT_HALFED
	if (mouses[0] or mouses[2]) and abs((mouse_x - cam_offset_x) - player.rect.centerx) < PLAYER_BREAK_BLOCK_DISTANCE_X and abs((mouse_y - cam_offset_y) - player.rect.centery) < PLAYER_BREAK_BLOCK_DISTANCE_Y:
		for block in block_group:
			if block.rect.collidepoint((mouse_x - cam_offset_x, mouse_y - cam_offset_y)):
				block.current_break_tick += player_break_speed * player_break_speed_modifier
				if block.current_break_tick >= block.tick_till_break:
					block.kill()

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
	for block in block_group:
		screen.blit(block.image, (round(block.rect.x + cam_offset_x), round(block.rect.y + cam_offset_y)))
	
	screen.blit(player.image, (round(player.rect.x + cam_offset_x), round(player.rect.y + cam_offset_y)))

	pygame.display.flip()


	# Debug
	if tick >= TARGET_TICK:
		print(f"FPS: {(TARGET_TICK) / time_passed if time_passed > 0 else 0:.2f} player:{player.rect.topleft} mouse:{mouse_x + cam_x - WIDTH_HALFED, mouse_y + cam_y - HEIGHT_HALFED}     ", end="\r")
		tick = 0
		time_passed = 0

	
	tick += 1
	dt = clock.tick(FPS) / 1000
	time_passed += dt

print("\n\n")
pygame.quit()
sys.exit()
