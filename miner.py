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

GRAVITY_SPEED = 10
MAX_VELOCITY = 1000

CAM_SPEED = 500.0

PLAYER_SPEED = 250.0
PLAYER_JUMP_SPEED = 320.0
PLAYER_MIN_VELOCITY = 10.0
PLAYER_WIDTH = 30
PLAYER_HEIGHT = 70

BLOCK_W = 50
BLOCK1_BREAK_TIME = 1 # in sec

MINE_AREA_W = 800
MINE_AREA_H = 1500
MINE_POS_X, MINE_POS_Y = -100, 400

N_PER_W = math.ceil(MINE_AREA_W / BLOCK_W)
N_PER_H = math.ceil(MINE_AREA_H / BLOCK_W)

class BlockSprite(pygame.sprite.Sprite):
	def __init__(self, color, size, pos, break_time):
		super().__init__()
		
		self.image = pygame.Surface(size)
		self.image.fill(color)
		
		self.rect = self.image.get_rect()
		self.rect.center = pos

		self.break_time = break_time

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

cam_x, cam_y = 0.0, 0.0
mouse_x, mouse_y = 0, 0

# Create Player
player = PlayerSprite((150, 50, 0), (PLAYER_WIDTH, PLAYER_HEIGHT), (0, 0))

moved_velocity_x = 0
moved_velocity_y = 0

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
TARGET_TICK = FPS // 4
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

	# Camera Movement
	dis = CAM_SPEED * dt
	dx, dy = 0, 0
	if keys[pygame.K_UP]:
		dy += dis
	if keys[pygame.K_DOWN]:
		dy -= dis

	if keys[pygame.K_LEFT]:
		dx += dis
	if keys[pygame.K_RIGHT]:
		dx -= dis
	
	cam_x += dx
	cam_y += dy

	# Player movement
	if keys[pygame.K_a]:
		moved_velocity_x = -PLAYER_SPEED

	if keys[pygame.K_d]:
		moved_velocity_x = PLAYER_SPEED

	if not (keys[pygame.K_a] or keys[pygame.K_d]):
		moved_velocity_x = 0

	if (keys[pygame.K_w] or keys[pygame.K_SPACE]) and airtime_tick <= 1:
		moved_velocity_y -= PLAYER_JUMP_SPEED
	
	moved_velocity_y += GRAVITY_SPEED
	moved_velocity_y = clamp(moved_velocity_y, -MAX_VELOCITY, MAX_VELOCITY)


	# Position update and collision check
	player.rect.x += moved_velocity_x * dt
	for block in block_group:
		is_collide = pygame.Rect.colliderect(player.rect , block.rect)
		if is_collide:
			if moved_velocity_x > 0:
				player.rect.right = block.rect.left
				moved_velocity_x = 0
			elif moved_velocity_x < 0:
				player.rect.left = block.rect.right
				moved_velocity_x = 0

	player.rect.y += moved_velocity_y * dt
	for block in block_group:
		is_collide = pygame.Rect.colliderect(player.rect , block.rect)
		if is_collide:
			if moved_velocity_y > 0:
				player.rect.bottom = block.rect.top
				moved_velocity_y = 0
				airtime_tick = 0
			elif moved_velocity_x < 0:
				player.rect.top = block.rect.bottom
				moved_velocity_y = 0

	# Drawing
	for block in block_group:
		x, y = block.rect.center
		screen.blit(block.image, (round(block.rect.x + cam_x), round(block.rect.y + cam_y)))
	
	screen.blit(player.image, (round(player.rect.x + cam_x), round(player.rect.y + cam_y)))

	pygame.display.flip()


	if tick >= TARGET_TICK:
		print(f"FPS: {1 / dt if dt > 0 else 0:.2f} Velocity: ({moved_velocity_x}, {moved_velocity_y})     ", end="\r")
		tick = 0
	tick += 1
	airtime_tick += 1
	dt = clock.tick(FPS) / 1000

pygame.quit()
sys.exit()
