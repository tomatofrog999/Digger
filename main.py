import pygame
import sys
import math
import random as r

def clamp(val, min_val, max_val):
	return min(max(val, min_val), max_val)

# Constant
WIDTH = 800
HEIGHT = 600
FPS = 60
TARGET_TICK = FPS // 4

GRAVITY_SPEED = 10
MAX_VELOCITY = 1000

BLOCK_W = 50
BLOCK1_BREAK_TIME = 0.2 # in sec

MINE_AREA_W = 800
MINE_AREA_H = 1500
MINE_POS_X, MINE_POS_Y = -100, 400

N_PER_W = math.ceil(MINE_AREA_W / BLOCK_W)
N_PER_H = math.ceil(MINE_AREA_H / BLOCK_W)

PLAYER_SPEED = 250.0
PLAYER_JUMP_SPEED = 230.0
PLAYER_MIN_VELOCITY = 10.0
PLAYER_WIDTH = 30
PLAYER_HEIGHT = 70
PLAYER_BREAK_BLOCK_DISTANCE_X = 2 * BLOCK_W + PLAYER_WIDTH // 2
PLAYER_BREAK_BLOCK_DISTANCE_Y = 2 * BLOCK_W + PLAYER_HEIGHT // 2

CAM_SPEED = 900.0
CAM_SPEED_SCALE = 5.0 # per distance(pixel)
CAM_MIN_DISTANCE = 5

class BlockSprite(pygame.sprite.Sprite):
	break_time = 0
	break_tick = 0.0
	def __init__(self, color, size, pos, break_time):
		super().__init__()
		
		self.image = pygame.Surface(size)
		self.image.fill(color)
		
		self.rect = self.image.get_rect()
		self.rect.center = pos

		self.break_time = break_time
		self.break_tick = 0.0

class PlayerSprite(pygame.sprite.Sprite):
	def __init__(self, color, size, pos):
		super().__init__()
		
		self.image = pygame.Surface(size)
		self.image.fill(color)
		
		self.rect = self.image.get_rect()
		self.rect.center = pos

# Initialization
pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mining Game")
clock = pygame.time.Clock()

cam_x, cam_y = 0, 0
mouse_x, mouse_y = 0, 0

# Create Player
player = PlayerSprite((150, 50, 0), (PLAYER_WIDTH, PLAYER_HEIGHT), (0, 0))

player_break_speed_modifier = 1

player_velocity_x = 0
player_velocity_y = 0

# Create block group
block_group = pygame.sprite.Group()
block_x, block_y = 0, 0
for i in range(N_PER_W):
	for j in range(N_PER_H):
		block = BlockSprite((0, r.randint(0,255), r.randint(0,255)), (BLOCK_W, BLOCK_W), (round(block_x + MINE_POS_X), round(block_y + MINE_POS_Y)), BLOCK1_BREAK_TIME)
		block_group.add(block)
		block_y += BLOCK_W
	block_x += BLOCK_W
	block_y = 0
print("size:", len(block_group))

dt = 0
tick = 0
airtime_tick = 0
running = True
while running:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
		elif event.type == pygame.MOUSEMOTION:
			mouse_x, mouse_y = event.pos
	
	screen.fill("black")

	keys = pygame.key.get_pressed()
	mouses = pygame.mouse.get_pressed()

	# Player movement
	if keys[pygame.K_a]:
		player_velocity_x = -PLAYER_SPEED

	if keys[pygame.K_d]:
		player_velocity_x = PLAYER_SPEED

	if not (keys[pygame.K_a] or keys[pygame.K_d]):
		player_velocity_x = 0

	if (keys[pygame.K_w] or keys[pygame.K_SPACE]) and airtime_tick <= 1:
		player_velocity_y -= PLAYER_JUMP_SPEED
	
	player_velocity_y += GRAVITY_SPEED
	player_velocity_y = clamp(player_velocity_y, -MAX_VELOCITY, MAX_VELOCITY)


	# Position update and collision check
	player.rect.x += player_velocity_x * dt
	for block in block_group:
		is_collide = pygame.Rect.colliderect(player.rect , block.rect)
		if is_collide:
			if player_velocity_x > 0:
				player.rect.right = block.rect.left
				player_velocity_x = 0
			elif player_velocity_x < 0:
				player.rect.left = block.rect.right
				player_velocity_x = 0

	player.rect.y += player_velocity_y * dt
	for block in block_group:
		is_collide = pygame.Rect.colliderect(player.rect , block.rect)
		if is_collide:
			if player_velocity_y > 0:
				player.rect.bottom = block.rect.top
				player_velocity_y = 0
				airtime_tick = 0
			elif player_velocity_y < 0:
				player.rect.top = block.rect.bottom
				player_velocity_y = 0

	# Break block
	if mouses[0] and abs((mouse_x + cam_x) - player.rect.centerx) < PLAYER_BREAK_BLOCK_DISTANCE_X and abs((mouse_y + cam_y) - player.rect.centery) < PLAYER_BREAK_BLOCK_DISTANCE_Y:
		for block in block_group:
			if block.rect.collidepoint((mouse_x + cam_x, mouse_y + cam_y)):
				block.break_tick += 1 * player_break_speed_modifier
				if block.break_tick >= BLOCK1_BREAK_TIME * FPS:
					block.kill()

	# Camera Movement
	cam_displacement_x = player.rect.centerx - (cam_x + WIDTH / 2)
	cam_displacement_y = player.rect.centery - (cam_y + HEIGHT / 2)
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
		screen.blit(block.image, (round(block.rect.x - cam_x), round(block.rect.y - cam_y)))
	
	screen.blit(player.image, (round(player.rect.x - cam_x), round(player.rect.y - cam_y)))

	pygame.display.flip()


	if tick >= TARGET_TICK:
		print(f"FPS: {1 / dt if dt > 0 else 0:.2f} pos: {player.rect.center} m: {(mouse_x + cam_x, mouse_y + cam_y)}     ", end="\r")
		tick = 0
	tick += 1
	airtime_tick += 1
	dt = clock.tick(FPS) / 1000

print("\n\n")
pygame.quit()
sys.exit()
