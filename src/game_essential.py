import pygame
import random as r
from enum import Enum
import itertools
import math
import json
from game_constant import *

class Block(pygame.sprite.Sprite):
	HEALTH_TO_BLOCK_RATE = 1 / 3 
	def __init__(self, surface: pygame.Surface, topleft: tuple[int, int], max_health: float, flip_x: bool, flip_y: bool, multi_block: bool, energy_usage: int):
		super().__init__()
		surface = pygame.transform.flip(surface, flip_x, flip_y)

		if multi_block:
			self.image = scale_surface(surface, 2)
		else:
			self.image = surface
		
		self.rect = self.image.get_rect()
		self.multi_block = multi_block

		self.get_rect().topleft = topleft

		self.max_health = max_health

		self.damage_taken = 0.0

		self.gain_block = round(self.max_health * Block.HEALTH_TO_BLOCK_RATE)

		self.energy_usage = energy_usage

		self.position_index: tuple[int, int] | None = None

	def set_position_index(self, position_index: tuple[int, int]):
		self.position_index = position_index

	def check_damage(self, value: float) -> bool:
		return self.damage_taken + value >= self.max_health

	def destroy(self, player_stats: PlayerStats):
		super().kill()
		player_stats.add_block(self.gain_block)

	def get_rect(self) -> pygame.Rect:
		if not isinstance(self.rect, pygame.Rect):
			raise TypeError("'rect' variable need to be pygame.Rect type.")
		return self.rect

class BombBlock(Block):
	def __init__(self, surface: pygame.Surface, topleft: tuple[int, int], flip_x: bool, flip_y: bool, bomb_damage: int, energy_usage: int):
		super().__init__(surface, topleft, 0, flip_x, flip_y, False, energy_usage)
		self.bomb_damage = bomb_damage
		self.gain_block = 0

	def destroy(self, player_stats: PlayerStats):
		super().kill()
		player_stats.remove_health(self.bomb_damage)

	def get_rect(self) -> pygame.Rect:
		if not isinstance(self.rect, pygame.Rect):
			raise TypeError("'rect' variable need to be pygame.Rect type.")
		return self.rect

class EnergyBlock(Block):
	def __init__(self, surface: pygame.Surface, topleft: tuple[int, int], max_health: float, flip_x: bool, flip_y: bool, energy_addition: int, multi_block: bool, energy_usage: int):
		super().__init__(surface, topleft, max_health * 1 if not multi_block else 2, flip_x, flip_y, multi_block, energy_usage)
		self.energy_addition = energy_addition
		self.gain_block = 0
		self.gain_energy = self.energy_addition * 1 if not self.multi_block else 4

	def destroy(self, player_stats: PlayerStats):
		super().kill()
		player_stats.add_energy(self.gain_energy)

	def get_rect(self) -> pygame.Rect:
		if not isinstance(self.rect, pygame.Rect):
			raise TypeError("'rect' variable need to be pygame.Rect type.")
		return self.rect

class TreasureBlock(Block):
	def __init__(self, surface: pygame.Surface, topleft: tuple[int, int], max_health: float, flip_x: bool, flip_y: bool, money_addition: int, multi_block: bool, energy_usage: int):
		super().__init__(surface, topleft, max_health * 1 if not multi_block else 2, flip_x, flip_y, multi_block, energy_usage)
		self.money_addition = money_addition

	def destroy(self, player_stats: PlayerStats):
		super().kill()
		player_stats.add_money(self.money_addition * 1 if not self.multi_block else 4)

	def get_rect(self) -> pygame.Rect:
		if not isinstance(self.rect, pygame.Rect):
			raise TypeError("'rect' variable need to be pygame.Rect type.")
		return self.rect

class PlatformSprite(pygame.sprite.Sprite):
	def __init__(self, surface: pygame.Surface, topleft: tuple[int, int]):
		super().__init__()

		self.image = surface
		
		self.rect = self.image.get_rect()
		self.rect.topleft = topleft

	def get_rect(self) -> pygame.Rect:
		if not isinstance(self.rect, pygame.Rect):
			raise TypeError("'rect' variable need to be pygame.Rect type.")
		return self.rect

class PlayerStats:
	def __init__(self):
		self.max_health = -1
		self.health = -1
		self.max_energy = -1
		self.energy = -1
		self.block = 0
		self.max_block = -1
		self.money = 0
		self.rate_of_convertion = -1.0

		self.break_damage = -1.0
		self.break_damage_modifier = -1.0
		self.on_beat_extra_damage = -1.0
		self.on_beat_extra_damage_modifier = -1.0
		self.owned_item = []

		self.game_over = False

	def to_dict(self):
		return \
		{
			"max_health": self.max_health,
            "health": self.health,
            "max_energy": self.max_energy,
            "energy": self.energy,
            "block": self.block,
            "max_block": self.max_block,
            "money": self.money,
            "rate_of_convertion": self.rate_of_convertion,
            "break_damage": self.break_damage,
            "break_damage_modifier": self.break_damage_modifier,
            "on_beat_extra_damage": self.on_beat_extra_damage,
            "on_beat_extra_damage_modifier": self.on_beat_extra_damage_modifier,
            "owned_item": self.owned_item
		}

	def load_dict(self, new_player_stats: dict[str, int | float | list]):
		if any([stats not in new_player_stats for stats in ("max_health", "health", "max_energy", "energy",\
					"block", "max_block", "money", "rate_of_convertion", "break_damage", "break_damage_modifier", \
					"on_beat_extra_damage", "on_beat_extra_damage_modifier", "owned_item")]) \
				or not isinstance(new_player_stats["max_health"], int) \
				or not isinstance(new_player_stats["health"], int) \
				or not isinstance(new_player_stats["max_energy"], int) \
				or not isinstance(new_player_stats["energy"], int) \
				or not isinstance(new_player_stats["block"], int) \
				or not isinstance(new_player_stats["max_block"], int) \
				or not isinstance(new_player_stats["money"], int) \
				or not isinstance(new_player_stats["rate_of_convertion"], float) \
				or not isinstance(new_player_stats["break_damage"], float) \
				or not isinstance(new_player_stats["break_damage_modifier"], float) \
				or not isinstance(new_player_stats["on_beat_extra_damage"], float) \
				or not isinstance(new_player_stats["on_beat_extra_damage_modifier"], float) \
				or not isinstance(new_player_stats["owned_item"], list):
			raise ValueError("Unable to load from dict.")
		self.max_health = new_player_stats["max_health"]
		self.health = new_player_stats["health"]
		self.max_energy = new_player_stats["max_energy"]
		self.energy = new_player_stats["energy"]
		self.block = new_player_stats["block"]
		self.max_block = new_player_stats["max_block"]
		self.money = new_player_stats["money"]
		self.rate_of_convertion = new_player_stats["rate_of_convertion"]
		self.break_damage = new_player_stats["break_damage"]
		self.break_damage_modifier = new_player_stats["break_damage_modifier"]
		self.on_beat_extra_damage = new_player_stats["on_beat_extra_damage"]
		self.on_beat_extra_damage_modifier = new_player_stats["on_beat_extra_damage_modifier"]
		self.owned_item = new_player_stats["owned_item"]

	def reset(self):
		self.init_break_damage(START_BREAK_DAMAGE, START_BREAK_DAMAGE_MODIFIER).init_max_block(START_MAX_INVENTORY) \
			.init_max_energy(START_ENERGY).init_max_health(START_HEALTH).init_on_beat_constant(START_ON_BEAT_EXTRA_DMG, START_ON_BEAT_EXTRA_DMG_MODIFIER) \
			.init_rate_of_convertion(START_RATE_OF_CONVERTION)
		self.check_init()

	def check_init(self):
		required_attrs = [
			'max_health',
			'health',
			'max_energy',
			'energy',
			'max_block',
			'money',
			'rate_of_convertion',
			'break_damage',
			'break_damage_modifier',
			'on_beat_extra_damage',
			'on_beat_extra_damage_modifier'
		]
		check_initialization(self, required_attrs)

	def init_max_health(self, max_health: int):
		self.max_health = max_health
		self.health = max_health
		return self
	
	def init_max_energy(self, max_energy: int):
		self.max_energy = max_energy
		self.energy = max_energy
		return self

	def init_max_block(self, max_block: int):
		self.max_block = max_block
		return self

	def init_rate_of_convertion(self, rate_of_convertion: float):
		self.rate_of_convertion = rate_of_convertion
		return self

	def init_break_damage(self, break_damage: float, break_damage_modifier: float):
		self.break_damage = break_damage
		self.break_damage_modifier = break_damage_modifier
		return self

	def init_on_beat_constant(self, on_beat_extra_damage: float, on_beat_extra_damage_modifier: float):
		self.on_beat_extra_damage = on_beat_extra_damage
		self.on_beat_extra_damage_modifier = on_beat_extra_damage_modifier
		return self

	def refill_energy(self):
		self.energy = self.max_energy

	def add_block(self, amount: int):
		if amount < 0:
			raise ValueError("Amount cannot be negative for add_block function.")
		self.block = min(self.block + amount, self.max_block)

	def remove_block(self, amount: int):
		if amount < 0:
			raise ValueError("Amount cannot be negative for remove_block function.")
		self.block = max(0, self.block - amount)

	def add_energy(self, amount: int):
		if amount < 0:
			raise ValueError("Amount cannot be negative for add_energy function.")
		self.energy = min(self.energy + amount, self.max_energy)

	def remove_energy(self, amount: int) -> bool:
		if amount < 0:
			raise ValueError("Amount cannot be negative for remove_energy function.")
		new_amount = self.energy - amount
		if new_amount < 0:
			return False
		else:
			self.energy = new_amount
			return True

	def add_money(self, amount: int):
		if amount < 0:
			raise ValueError("Amount cannot be negative for add_money function.")
		self.money = self.money + amount
	
	def remove_money(self, amount: int):
		if amount < 0:
			raise ValueError("Amount cannot be negative for remove_money function.")
		new_amount = self.money - amount
		if new_amount < 0:
			return False
		else:
			self.money = new_amount
			return True
	
	def add_health(self, amount: int):
		if amount < 0:
			raise ValueError("Amount cannot be negative for add_health function.")
		self.health = min(self.health + amount, self.max_health)

	def remove_health(self, amount: int):
		if amount < 0:
			raise ValueError("Amount cannot be negative for remove_health function.")
		self.health = max(0, self.health - amount)
		if self.health == 0:
			self.gameover()

	def gameover(self):
		self.game_over = True

	def convert_block_to_money(self):
		self.money += round(self.block * self.rate_of_convertion)
		self.block = 0

class PlayerSprite(pygame.sprite.Sprite):
	class AnimationData:
		def __init__(self, start_index: int, step: int, cooldown_ms: int, loop: bool, priority: int):
			self.start_index = start_index
			self.step = step
			self.cooldown_ms = cooldown_ms
			self.loop = loop
			self.priority = priority
			self.surfaces: tuple[pygame.Surface, ...] = ()

	class AnimationState(Enum):
		IDLE = 0
		WALK = 1
		JUMP = 2
		FALL = 3
		DIG = 4
		WALL_JUMP = 5
		WALL_SLIDE = 6

	class TouchWallState(Enum):
		NOT_TOUCH_WALL = 0
		TOUCH_WALL_RIGHT = 1
		TOUCH_WALL_LEFT = 2

	class DirectionState(Enum):
		UP = 0
		DOWN = 1
		RIGHT = 2
		LEFT = 3

	WALK_ACCELERATION = 500.0
	SLOW_DOWN_ACCELERATION = 400.0
	MAX_WALK_SPEED = 300.0

	MAX_SIDE_SPEED = 1200.0
	MAX_DOWN_SPEED = 1200.0
	MAX_UP_SPEED = 500.0

	# v^2 = u^2 + 2as u = sqrt(2as)
	# can jump up 2 block 
	# s = block height * 2
	JUMP_SPEED = math.sqrt(2 * GRAVITY_ACCELERATION * ((BLOCK_HEIGHT + 5) * 2))
	WALL_KICK_SPEED = 150.0
	WALL_SLIDE_ACCELERATION = GRAVITY_ACCELERATION * 3 / 2
	WALL_SLIDE_SPEED_THRESHOLD = 100.0
	TICK_TILL_ENABLE_SLIDE = round(0.1 * FPS)

	BREAK_BLOCK_DISTANCE = 3 # block
	ADDITION_SPEED_WHEN_BREAK_BLOCK = 200.0
	def __init__(self, topleft: tuple[float, float], hitblock_size: tuple[int, int], player_stats: PlayerStats):
		super().__init__()
		self.image_offset: tuple[int, int] = (0,0)

		self.player_stats: PlayerStats = player_stats
		self.animation_dict: dict[PlayerSprite.AnimationState, PlayerSprite.AnimationData] | None = None
		self.last_action: PlayerSprite.AnimationState = PlayerSprite.AnimationState.IDLE
		self.action: PlayerSprite.AnimationState = PlayerSprite.AnimationState.IDLE
		self.update_animation_time = 0
		self.animation_frame = 0
		self.breakable_group: pygame.sprite.Group[Block] | None = None
		self.unbreakable_group: pygame.sprite.Group | None = None
		self.screen: pygame.Surface | None = None

		self.touch_wall_side = PlayerSprite.TouchWallState.NOT_TOUCH_WALL
		self.facing_left = False # For movement and surface mirroring
		self.facing_direction = PlayerSprite.DirectionState.DOWN # For diging direction
		self.on_beat_hit = False
	
		self.airtime_tick = 0
		self.touch_wall_tick = 0
	
		self.velocity_x = 0.0
		self.velocity_y = 0.0

		self.rect = pygame.FRect(topleft, hitblock_size)

		self.origin_break_block_point_x = BLOCK_WIDTH // 2 + self.get_rect().width // 2
		self.origin_break_block_point_y = BLOCK_HEIGHT // 2 + self.get_rect().height // 2

	def check_init(self):
		required_attrs = [
			'animation_dict', 'breakable_group', 'unbreakable_group', 'screen'
		]
		check_initialization(self, required_attrs)
	
	def init_animation_data(self, animation_data: dict[AnimationState, AnimationData]):
		self.animation_dict = animation_data
		if PlayerSprite.AnimationState.IDLE not in animation_data:
			raise ValueError("Animation data should have atleast an idle state.")
		return self

	def init_screen(self, screen: pygame.Surface):
		self.screen = screen
		return self

	def init_image_offset(self, offset: tuple[int, int]):
		self.image_offset = offset
		return self

	def init_breakable_group(self, breakable_group: pygame.sprite.Group):
		self.breakable_group = breakable_group
		return self

	def init_unbreakable_group(self, unbreakable_group: pygame.sprite.Group):
		self.unbreakable_group = unbreakable_group
		return self

	def get_rect(self) -> pygame.FRect:
		if not isinstance(self.rect, pygame.FRect):
			raise TypeError("'rect' variable need to be pygame.FRect type.")
		return self.rect

	def get_animation_dict(self) -> dict[AnimationState, AnimationData]:
		if not isinstance(self.animation_dict, dict):
			raise TypeError("'animation_data' variable need to be dict type.")
		return self.animation_dict

	def get_animation_data(self, state: AnimationState) -> PlayerSprite.AnimationData:
		animation_dict = self.get_animation_dict()
		if not state in animation_dict:
			return animation_dict[PlayerSprite.AnimationState.IDLE]
		return animation_dict[state]
	
	def get_breakable_group(self) -> pygame.sprite.Group[Block]:
		if not isinstance(self.breakable_group, pygame.sprite.Group):
			raise TypeError("'breakable_group' variable need to be pygame.sprite.Group type.")
		return self.breakable_group

	def get_unbreakable_group(self) -> pygame.sprite.Group:
		if not isinstance(self.unbreakable_group, pygame.sprite.Group):
			raise TypeError("'unbreakable_group' variable need to be pygame.sprite.Group type.")
		return self.unbreakable_group

	def set_surface(self, animation_surface: pygame.Surface, size_per_image: tuple[int, int], surface_scale: int):
		for animation in self.get_animation_dict().values():
			temp_list = []
			for i in range(animation.start_index, animation.start_index + animation.step):
				temp_list.append(get_surface_from_sprite_sheet(animation_surface, (i, 0), size_per_image, surface_scale, True))
			animation.surfaces = tuple(temp_list)
		default_animation = self.get_animation_data(PlayerSprite.AnimationState.IDLE)
		self.image = default_animation.surfaces[0]

	def change_action(self, new_action: AnimationState, forced: bool = False):
		animation = self.get_animation_data(self.action)
		new_animation = self.get_animation_data(new_action)
		if forced or new_animation.priority >= animation.priority:
			self.action = new_action
	
	def draw(self, camera_offset: tuple[float | int, float | int]):
		current_time = pygame.time.get_ticks()

		animation = self.get_animation_data(self.action)
		if self.action != self.last_action:
			self.last_action = self.action
			self.animation_frame = 0
			self.update_animation_time = current_time + animation.cooldown_ms

		surf = animation.surfaces[self.animation_frame]

		if self.facing_left:
			surf = pygame.transform.flip(surf, True, False)

		left, top = self.get_rect().topleft
		left += camera_offset[0]
		top += camera_offset[1]

		if not isinstance(self.screen, pygame.Surface):
			raise TypeError("'screen' variable need to be pygame.Surface Type.")
		self.screen.blit(surf, (round(left + self.image_offset[0]), round(top + self.image_offset[1])))
		
		if current_time >= self.update_animation_time:
			self.update_animation_time = current_time + animation.cooldown_ms
			if animation.loop:
				self.animation_frame = (self.animation_frame + 1) if self.animation_frame < len(animation.surfaces) - 1 else 0
			else:
				if self.animation_frame >= len(animation.surfaces) - 1:
					self.change_action(PlayerSprite.AnimationState.IDLE, forced=True)
				else:
					self.animation_frame += 1

	def handle_movement(self, keys: pygame.key.ScancodeWrapper, events: list[pygame.Event], delta_time: float):
		space_pressed = False
		j_pressed = False
		k_pressed = False
				
		for event in events:
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_SPACE:
					space_pressed = True
				if event.key == pygame.K_j:
					j_pressed = True
				if event.key == pygame.K_k:
					k_pressed = True
		
		a_pressed = keys[pygame.K_a]
		d_pressed = keys[pygame.K_d]

		# Player movement
		if (a_pressed or d_pressed) and not (a_pressed and d_pressed) and not (j_pressed or k_pressed):
			if a_pressed:
				self.facing_left = True
				temp_velocity = -PlayerSprite.WALK_ACCELERATION * delta_time
				temp_velocity = clamp(-PlayerSprite.MAX_WALK_SPEED - self.velocity_x, temp_velocity, 0)
			else:
				self.facing_left = False
				temp_velocity = PlayerSprite.WALK_ACCELERATION * delta_time
				temp_velocity = clamp(PlayerSprite.MAX_WALK_SPEED - self.velocity_x, 0, temp_velocity)
			self.velocity_x += temp_velocity

			self.change_action(PlayerSprite.AnimationState.WALK)
		elif self.velocity_x != 0:
			self.velocity_x -= extract_number_sign(self.velocity_x) * min(abs(self.velocity_x), PlayerSprite.SLOW_DOWN_ACCELERATION * delta_time)
		else:
			self.change_action(PlayerSprite.AnimationState.IDLE)
		self.velocity_x = clamp(self.velocity_x, -PlayerSprite.MAX_SIDE_SPEED, PlayerSprite.MAX_SIDE_SPEED)
	
		can_wall_sliding = self.touch_wall_tick >= PlayerSprite.TICK_TILL_ENABLE_SLIDE and self.airtime_tick > PlayerSprite.TICK_TILL_ENABLE_SLIDE
		if space_pressed and (self.airtime_tick <= 0 or can_wall_sliding) and not (j_pressed or k_pressed):
			if can_wall_sliding and self.touch_wall_side != PlayerSprite.TouchWallState.NOT_TOUCH_WALL:
				if self.touch_wall_side == PlayerSprite.TouchWallState.TOUCH_WALL_LEFT:
					self.velocity_x += PlayerSprite.WALL_KICK_SPEED
				else:
					self.velocity_x -= PlayerSprite.WALL_KICK_SPEED
				self.touch_wall_tick = 0
				self.change_action(PlayerSprite.AnimationState.WALL_JUMP)
			else:
				self.change_action(PlayerSprite.AnimationState.JUMP)
			self.velocity_y -= PlayerSprite.JUMP_SPEED
	
		if can_wall_sliding and self.velocity_y > PlayerSprite.WALL_SLIDE_SPEED_THRESHOLD:
			self.velocity_y -= PlayerSprite.WALL_SLIDE_ACCELERATION * delta_time
		if can_wall_sliding:
			self.change_action(PlayerSprite.AnimationState.WALL_SLIDE)
		elif self.action == PlayerSprite.AnimationState.WALL_SLIDE and not can_wall_sliding:
			self.change_action(PlayerSprite.AnimationState.IDLE, forced=True)
	
		self.velocity_y += GRAVITY_ACCELERATION * delta_time
		self.velocity_y = clamp(self.velocity_y, -PlayerSprite.MAX_UP_SPEED, PlayerSprite.MAX_DOWN_SPEED)

	def update_position_and_collision(self, delta_time: float):
		self.touch_wall_side = PlayerSprite.TouchWallState.NOT_TOUCH_WALL
		srect = self.get_rect()
		srect.x += self.velocity_x * delta_time
		if self.velocity_x != 0:
			for block in itertools.chain(self.get_breakable_group(), self.get_unbreakable_group()):
				if srect.colliderect(block.get_rect()):
					if self.velocity_x > 0:
						srect.right = block.get_rect().left
						self.touch_wall_side = PlayerSprite.TouchWallState.TOUCH_WALL_RIGHT
					else:
						srect.left = block.get_rect().right
						self.touch_wall_side = PlayerSprite.TouchWallState.TOUCH_WALL_LEFT
					self.velocity_x = 0
					break
		if self.touch_wall_side == PlayerSprite.TouchWallState.NOT_TOUCH_WALL:
			self.touch_wall_tick = 0
		else:
			self.touch_wall_tick += 1
	
		srect.y += self.velocity_y * delta_time
		self.touch_ground = False
		if self.velocity_y != 0:
			for block in itertools.chain(self.get_breakable_group(), self.get_unbreakable_group()):
				if srect.colliderect(block.get_rect()):
					if self.velocity_y > 0:
						srect.bottom = block.get_rect().top
						self.touch_ground = True
						self.airtime_tick = 0
						if self.action in (PlayerSprite.AnimationState.JUMP, PlayerSprite.AnimationState.FALL, PlayerSprite.AnimationState.WALL_SLIDE):
							self.change_action(PlayerSprite.AnimationState.IDLE, forced=True)
					else:
						srect.top = block.get_rect().bottom
					self.velocity_y = 0
					break
		if not self.touch_ground:
			self.airtime_tick += 1
			self.change_action(PlayerSprite.AnimationState.FALL)

	def handle_break_block(self, keys: pygame.key.ScancodeWrapper, events: list[pygame.Event], game_state: GameState):
		j_pressed = False
		k_pressed = False
		for event in events:
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_j:
					j_pressed = True
				if event.key == pygame.K_k:
					k_pressed = True
	
		a_pressed = keys[pygame.K_a]
		d_pressed = keys[pygame.K_d]
		w_pressed = keys[pygame.K_w]
		s_pressed = keys[pygame.K_s]

		not_diagonally = not ((w_pressed or s_pressed) and (a_pressed or d_pressed))

		if not_diagonally:
			if not (w_pressed and d_pressed):
				if w_pressed:
					self.facing_direction = PlayerSprite.DirectionState.UP
				elif s_pressed:
					self.facing_direction = PlayerSprite.DirectionState.DOWN

			if not (a_pressed and d_pressed):
				if a_pressed:
					self.facing_direction = PlayerSprite.DirectionState.LEFT
				elif d_pressed:
					self.facing_direction = PlayerSprite.DirectionState.RIGHT

		if (j_pressed or k_pressed) and not_diagonally:
			digging_offset_x = 0
			digging_offset_y = 0
			if w_pressed or s_pressed or a_pressed or d_pressed:
				if w_pressed:
					digging_offset_y -= self.origin_break_block_point_y
					self.facing_direction = PlayerSprite.DirectionState.UP
				if s_pressed:
					digging_offset_y += self.origin_break_block_point_y
					self.facing_direction = PlayerSprite.DirectionState.DOWN
			
				if a_pressed:
					digging_offset_x -= self.origin_break_block_point_x
					self.facing_direction = PlayerSprite.DirectionState.LEFT
				if d_pressed:
					digging_offset_x += self.origin_break_block_point_x
					self.facing_direction = PlayerSprite.DirectionState.RIGHT
			else:
				if self.facing_direction == PlayerSprite.DirectionState.UP:
					digging_offset_y -= self.origin_break_block_point_y
				elif self.facing_direction == PlayerSprite.DirectionState.DOWN:
					digging_offset_y += self.origin_break_block_point_y

				elif self.facing_direction == PlayerSprite.DirectionState.LEFT:
					digging_offset_x -= self.origin_break_block_point_x
				elif self.facing_direction == PlayerSprite.DirectionState.RIGHT:
					digging_offset_x += self.origin_break_block_point_x
	
			is_collide = False
			srect = self.get_rect()
			for _ in range(PlayerSprite.BREAK_BLOCK_DISTANCE):
				for block in self.breakable_group or ():
					is_collide = block.get_rect().collidepoint((srect.centerx + digging_offset_x, srect.centery + digging_offset_y))
					if is_collide:
						# not remove energy when hit on beat
						if not self.on_beat_hit and not self.player_stats.remove_energy(block.energy_usage):
							raise ValueError("Energy not enough")
						self.change_action(PlayerSprite.AnimationState.DIG)
						if self.on_beat_hit:
							damage_deal = (self.player_stats.break_damage + self.player_stats.on_beat_extra_damage) * (self.player_stats.break_damage_modifier + self.player_stats.on_beat_extra_damage_modifier)
						else:
							damage_deal = self.player_stats.break_damage * self.player_stats.break_damage_modifier
						block_break = block.check_damage(damage_deal)

						if block_break and self.player_stats.block >= self.player_stats.max_block and block.gain_block > 0:
							raise ValueError("Inventory full")
						
						block.damage_taken += damage_deal
						
						if block_break:	
							if digging_offset_x != 0:
								self.velocity_x += extract_number_sign(digging_offset_x) * PlayerSprite.ADDITION_SPEED_WHEN_BREAK_BLOCK
							if digging_offset_y > 0:
								self.velocity_y += PlayerSprite.ADDITION_SPEED_WHEN_BREAK_BLOCK
							pos_index = block.position_index
							if pos_index != None:
								game_state.block_broken.append(pos_index)
							block.destroy(self.player_stats)
						break
				if is_collide:
					break
				if digging_offset_x != 0 and digging_offset_y == 0:
					digging_offset_x += extract_number_sign(digging_offset_x) * BLOCK_WIDTH
				elif digging_offset_y != 0 and digging_offset_x == 0:
					digging_offset_y += extract_number_sign(digging_offset_y) * BLOCK_HEIGHT
		return True

	def update(self, keys: pygame.key.ScancodeWrapper, events: list[pygame.Event], dt: float, game_state: GameState):
		self.handle_movement(keys, events, dt)
		self.update_position_and_collision(dt)
		try:
			self.handle_break_block(keys, events, game_state)
		except ValueError as e:
			print(str(e))
		

class BlockData:
	def __init__(self, surface: pygame.Surface, max_health: float, spawn_weight: float):
		self.surface = surface
		self.max_health = max_health
		self.spawn_weight = spawn_weight

class LayerData:
	def __init__(self, end_layer: int, block_tuple: tuple[BlockData, ...]):
		self.end_layer = end_layer
		self.block_tuple = block_tuple
		self.bomb_rate = -1
		self.bomb_damage = -1
		self.energy_rate = -1
		self.energy_addition = -1
		self.treasure_rate = -1
		self.treasure_addition = -1
		self.multiblock_rate = -1
		self.energy_usage = -1

		combined_weight = 0
		for x in self.block_tuple:
			combined_weight += x.spawn_weight

		if round(combined_weight, 4) != 1.0:
			raise ValueError("Combined weight of BlockData in LayerData is not 1.")

	def init_bomb(self, bomb_rate: float, bomb_damage: int):
		self.bomb_rate = bomb_rate
		self.bomb_damage = bomb_damage
		return self

	def init_energy(self, energy_rate: float, energy_addition: int):
		self.energy_rate = energy_rate
		self.energy_addition = energy_addition
		return self

	def init_treasure(self, treasure_rate: float, treasure_addition: int):
		self.treasure_rate = treasure_rate
		self.treasure_addition = treasure_addition
		return self

	def init_multiblock_rate(self, multiblock_rate: float):
		self.multiblock_rate = multiblock_rate
		return self

	def init_energy_usage(self, energy_usage: int):
		self.energy_usage = energy_usage
		return self

	def check_init(self):
		required_attrs = [
			'bomb_rate', 'bomb_damage', 'energy_rate', 'energy_addition', 'treasure_rate', 'treasure_addition', 'multiblock_rate', 'energy_usage'
		]
		check_initialization(self, required_attrs)

		if self.bomb_rate + self.energy_rate + self.treasure_rate > 1:
			raise ValueError("All combined spawn rate shouldn't exceed 1")

		if self.multiblock_rate > 1:
			raise ValueError("Multiblock rate shouldn't exceed 1")

	def get_random_block(self, rng: r.Random | None = None) -> BlockData:
		choosen = random_with_rate([x.spawn_weight for x in self.block_tuple], rng=rng)
		if choosen == -1:
			raise RuntimeError(f"Impossible state on get_random_block.")
		return self.block_tuple[choosen]
	

class MapData:
	def __init__(self, layer_tuple: tuple[LayerData, ...], block_width: int, block_height: int):
		self.layer_tuple = tuple(sorted(layer_tuple, key=(lambda x: x.end_layer)))
		self.block_width = block_width
		self.block_height = block_height

	def create_sprite_group(self, width: int, height: int, map_position: tuple[int, int], seed: int, ignored_block_index: list[tuple[int, int]] = []) -> pygame.sprite.Group[Block]:
		# by set the seed it will make random after run again to be the same if set to the same seed
		# that mean random after set the seed and run any random function 100 time and set the seed and run the 100 one again 
		# it will be the same in all 100 but if other place call random in between the 100 time it will make the result off
		local_rng = r.Random(seed)
		block_group = pygame.sprite.Group()
		block_x, block_y = 0, 0
		layer_index = 0
		layer = self.layer_tuple[layer_index]
		length = len(self.layer_tuple)
		multiblock_occupied_index: list[tuple[int, int]] = []
		for height_index in range(height):
			if height_index >= layer.end_layer:
				layer_index += 1
				if layer_index >= length:
					break
				layer = self.layer_tuple[layer_index]
			block_x = 0
			for width_index in range(width):
				if (width_index, height_index) in multiblock_occupied_index:
					block_x += self.block_width
					continue
				block_data = layer.get_random_block(rng=local_rng)
				choosen = random_with_rate((layer.bomb_rate, layer.energy_rate, layer.treasure_rate), rng=local_rng)
				multi_block = False
				if choosen != 0 and width_index + 1 < width and height_index + 1 < height \
						and all([pos_index not in multiblock_occupied_index for pos_index in [(width_index, height_index), (width_index + 1, height_index), (width_index, height_index + 1), (width_index + 1, height_index + 1)]]) \
						and height_index + 1 < layer.end_layer and local_rng.random() < layer.multiblock_rate:
					multi_block = True
					multiblock_occupied_index.extend([(width_index, height_index), (width_index + 1, height_index), (width_index, height_index + 1), (width_index + 1, height_index + 1)])

				# Placed after multi-block logic to ensure it will generate the same random result from seed 
				# and also to make it add occupied square for multi block so it not generate other block on the occupied square of multi-block
				if (width_index, height_index) in ignored_block_index:
					block_x += self.block_width
					continue

				if choosen == 0:
					bomb_block = pygame.Surface((self.block_width, self.block_height))
					bomb_block.fill("red")
					block = BombBlock(bomb_block, (block_x + map_position[0], block_y + map_position[1]), False, False, layer.bomb_damage, layer.energy_usage)
				elif choosen == 1:
					energy_block = pygame.Surface((self.block_width, self.block_height))
					energy_block.fill("green")
					block = EnergyBlock(energy_block, (block_x + map_position[0], block_y + map_position[1]), block_data.max_health / 2, False, False, layer.energy_addition, multi_block, layer.energy_usage)
				elif choosen == 2:
					treasure_block = pygame.Surface((self.block_width, self.block_height))
					treasure_block.fill("blue")
					block = TreasureBlock(treasure_block, (block_x + map_position[0], block_y + map_position[1]), block_data.max_health / 2, False, False, layer.treasure_addition, multi_block, layer.energy_usage)
				else:
					block = Block(block_data.surface, (block_x + map_position[0], block_y + map_position[1]), block_data.max_health, False, False, multi_block, layer.energy_usage)
				block.set_position_index((width_index, height_index))
				block_group.add(block)
				block_x += self.block_width
			block_y += self.block_height
		return block_group

class Camera:
	def __init__(self, x: float, y: float):
		self.x = x
		self.y = y

		self.cam_y_underground_offset = -1
		self.cam_speed_scale = -1
		self.mine_pos = (0, 0)
		self.cam_min_distance = -1
		self.screen_width_half = -1
		self.screen_height_half = -1

	def init_dynamic_camera_constant(self, cam_y_underground_offset: int, cam_speed_scale: float, mine_pos: tuple[int, int], cam_min_distance: float):
		self.cam_y_underground_offset = cam_y_underground_offset
		self.cam_speed_scale = cam_speed_scale
		self.mine_pos = mine_pos
		self.cam_min_distance = cam_min_distance
		return self

	def init_cam_offset(self, screen_width_half: int, screen_height_half: int):
		self.screen_width_half = screen_width_half
		self.screen_height_half = screen_height_half
		return self

	def check_init(self):
		required_attrs = [
			'cam_y_underground_offset', 'cam_speed_scale', 'cam_min_distance', 'screen_width_half', 'screen_height_half'
		]
		check_initialization(self, required_attrs)

	def get_cam_offset(self) -> tuple[float, float]:
		# When camera move, the object will move opposite camera. So, we negate the camera for x and y
		# Then we add half of screen to make camera focus on center of screen not on topleft of screen
		cam_offset_x = -self.x + self.screen_width_half
		cam_offset_y = -self.y + self.screen_height_half
		return (cam_offset_x, cam_offset_y)

	def update(self, player_rect: pygame.FRect, dt: float):
		cam_displacement_x = player_rect.x - self.x
		addition_height = self.cam_y_underground_offset if player_rect.bottom > self.mine_pos[1] else -self.cam_y_underground_offset
		cam_displacement_y = (player_rect.y + addition_height) - self.y
		cam_distance_x = abs(cam_displacement_x)
		cam_distance_y = abs(cam_displacement_y)
		if cam_displacement_x > self.cam_min_distance:
			self.x += min(cam_distance_x, self.cam_speed_scale * cam_distance_x * dt)
		elif cam_displacement_x < -self.cam_min_distance:
			self.x -= min(cam_distance_x, self.cam_speed_scale * cam_distance_x * dt)
		
		if cam_displacement_y > self.cam_min_distance:
			self.y += min(cam_distance_y, self.cam_speed_scale * cam_distance_y * dt)
		elif cam_displacement_y < -self.cam_min_distance:
			self.y -= min(cam_distance_y, self.cam_speed_scale * cam_distance_y * dt)

class RhythmHandler:
	LINE_WIDTH = 2
	def __init__(self, music_data_file: str, rhythm_error_margin_ms: int, width: int, height: int, rhythm_show_length_ms: int, wrong_press_cooldown_ms: int):
		self.screen_width_per_rhythm_length = width / rhythm_show_length_ms
		self.width = width
		self.height = height

		refined_rhythm_time = [] # (start, end, size)
		with open(music_data_file) as f:
			for line in f:
				line = line.strip()
				if (line != "" and line[0] == "#") or line == "":
					continue
				previous_rhythm = refined_rhythm_time[len(refined_rhythm_time) - 1] if len(refined_rhythm_time) > 0 else None
				current_rhythm_bound = float(line)
	
				# continuous front
				if previous_rhythm != None and previous_rhythm[1] > current_rhythm_bound - rhythm_error_margin_ms:
					lower = previous_rhythm[0]
					upper = current_rhythm_bound + rhythm_error_margin_ms
					refined_rhythm_time[len(refined_rhythm_time) - 1] = (lower, upper, upper - lower)
				else:
					lower = current_rhythm_bound - rhythm_error_margin_ms
					upper = current_rhythm_bound + rhythm_error_margin_ms
					refined_rhythm_time.append((lower, upper, upper - lower))
		self.rhythm_bound_tuple: tuple[tuple[int, int, int], ...] = tuple(refined_rhythm_time)

		temp_surf = []
		for rhythm in self.rhythm_bound_tuple:
			rhythm_surf = pygame.Surface((rhythm[2] * self.screen_width_per_rhythm_length, self.height))
			rhythm_surf.fill("purple")
			temp_surf.append(rhythm_surf)
		self.rhythm_surface_tuple: tuple[pygame.Surface, ...] = tuple(temp_surf)

		self.rhythm_index = 0
		self.wrong_press_next_reset = 0
		self.wrong_press_cooldown_ms = wrong_press_cooldown_ms
		self.current_music_time = 0
		self.screen: pygame.Surface | None = None
		self.line_offset_x = -1
		self.line_pos_ratio = -1.0
		self.topleft_pos = (0, 0)
		self.rhythm_show_length_ms = rhythm_show_length_ms

	def init_screen(self, screen: pygame.Surface, line_pos_ratio: float, center_pos: tuple[int, int] = (0, 0)):
		self.screen = screen
		self.topleft_pos = (center_pos[0] - self.width // 2, center_pos[1] - self.height // 2)
		self.line_offset_x = self.width * line_pos_ratio
		self.line_pos_ratio = line_pos_ratio
		return self

	def check_init(self):
		required_attrs = [
			'screen', 'line_offset_x', 'line_pos_ratio'
		]
		check_initialization(self, required_attrs)

	def get_screen(self) -> pygame.Surface:
		if not isinstance(self.screen, pygame.Surface):
			raise TypeError("'screen' variable need to be pygame.Surface type.")
		return self.screen

	def start(self, music_file: str, loudness: float):
		pygame.mixer.music.load(music_file)
		pygame.mixer.music.set_volume(loudness)
		pygame.mixer.music.play()

	def pause(self):
		pygame.mixer.music.pause()

	def unpause(self):
		pygame.mixer.music.unpause()

	def stop(self):
		pygame.mixer.music.stop()

	def update(self, player: PlayerSprite, pressed_dig: bool):
		if not pygame.mixer.music.get_busy():
			return
		self.current_music_time = pygame.mixer.music.get_pos()
		current_rhythm_bound = self.rhythm_bound_tuple[self.rhythm_index]

		while self.current_music_time > current_rhythm_bound[1]:
			player.on_beat_hit = False
			self.rhythm_surface_tuple[self.rhythm_index].fill("red")
			if self.rhythm_index + 1 < len(self.rhythm_surface_tuple):
				self.rhythm_index += 1
			else:
				self.rhythm_index = 0
				pygame.mixer.music.stop()
				for surface in self.rhythm_surface_tuple:
					surface.fill("purple")
				pygame.mixer.music.play()
				self.current_music_time = pygame.mixer.music.get_pos()
			current_rhythm_bound = self.rhythm_bound_tuple[self.rhythm_index]
		
		if pressed_dig and in_range(self.current_music_time, current_rhythm_bound[0], current_rhythm_bound[1]) and self.current_music_time > self.wrong_press_next_reset:
			self.rhythm_surface_tuple[self.rhythm_index].fill("green")
			player.on_beat_hit = True
			if self.rhythm_index + 1 < len(self.rhythm_surface_tuple):
				self.rhythm_index += 1
			else:
				rhythm_index = 0
				pygame.mixer.music.stop()
				for surface in self.rhythm_surface_tuple:
					surface.fill("purple")
				pygame.mixer.music.play()
				self.current_music_time = pygame.mixer.music.get_pos()

		if pressed_dig and not in_range(self.current_music_time, current_rhythm_bound[0], current_rhythm_bound[1]):
			self.wrong_press_next_reset = self.current_music_time + self.wrong_press_cooldown_ms

	def draw(self):
		screen = self.get_screen()
		left, top = self.topleft_pos
		point1 = (left, top)
		point2 = (left + self.width, top)
		point3 = (left, top + self.height)
		point4 = (left + self.width, top + self.height)
		pygame.draw.line(screen, "white", point1, point2, RhythmHandler.LINE_WIDTH)
		pygame.draw.line(screen, "white", point1, point3, RhythmHandler.LINE_WIDTH)
		pygame.draw.line(screen, "white", point2, point4, RhythmHandler.LINE_WIDTH)
		pygame.draw.line(screen, "white", point3, point4, RhythmHandler.LINE_WIDTH)
		for i in range(len(self.rhythm_surface_tuple)):
			# "refined_rhythm_time[i][0] - current_music_time" is delta time between start position of rhythm and current music time
			dt_rhythm_start = self.rhythm_bound_tuple[i][0] - self.current_music_time
			dt_rhythm_end = self.rhythm_bound_tuple[i][1] - self.current_music_time

			# culling surface that are not being render
			if dt_rhythm_start > self.rhythm_show_length_ms * (1 - self.line_pos_ratio):
				break
			if dt_rhythm_end < -self.rhythm_show_length_ms * self.line_pos_ratio:
				continue
			rhythm_position = dt_rhythm_start * self.screen_width_per_rhythm_length
			screen.blit(self.rhythm_surface_tuple[i], (rhythm_position + self.line_offset_x + self.topleft_pos[0], self.topleft_pos[1]))

		pygame.draw.line(screen, "white", (self.line_offset_x + self.topleft_pos[0], self.topleft_pos[1]), (self.line_offset_x + self.topleft_pos[0], self.height + self.topleft_pos[1]), RhythmHandler.LINE_WIDTH)

class GameState:
	MIN_SEED = -2**16
	MAX_SEED = 2**16 - 1
	def __init__(self, game_map: MapData, seed: int | None = None):
		self.game_map = game_map
		self.block_group: pygame.sprite.Group[Block] | None = None
		self.block_broken: list[tuple[int, int]] = []
		if seed == None:
			self.random_seed()
		else:
			self.seed = seed

	def random_seed(self):
		self.seed = r.randint(GameState.MIN_SEED, GameState.MAX_SEED)

	def reset_block_broken(self, player_sprite: PlayerSprite):
		self.block_broken = []
		self.create_new_block_group()
		player_sprite.breakable_group = self.block_group

	def get_block_group(self) -> pygame.sprite.Group[Block]:
		if not isinstance(self.block_group, pygame.sprite.Group):
			raise TypeError("'block_group' variable need to be pygame.sprite.Group type.")
		return self.block_group

	def create_new_block_group(self):
		self.block_group = self.game_map.create_sprite_group(BLOCK_PER_WIDTH, BLOCK_PER_HEIGHT, MINE_POS, self.seed, ignored_block_index=self.block_broken)

	def to_dict(self) -> dict[str, list[tuple[int, int]] | int]:
		return \
		{
			"block_broken": self.block_broken,
			"seed": self.seed
		}

	def load_dict(self, new_game_state: dict[str, list[list[int]] | int]):
		if "block_broken" not in new_game_state or "seed" not in new_game_state or not isinstance(new_game_state["block_broken"], list) or not isinstance(new_game_state["seed"], int):
			raise ValueError("Unable to load from dict.")

		block_broken = new_game_state["block_broken"]
		if len(block_broken) > 0 and len(block_broken[0]) == 2:
			self.block_broken = [(x[0], x[1]) for x in block_broken]
		else:
			self.block_broken = []
		
		self.seed = new_game_state["seed"]
		self.create_new_block_group()

def save_game(file_location: str, player_stats: PlayerStats, game_state: GameState):
	save_dict = \
	{
		"save_version": SAVE_VERSION, 
	    "save_data": 
		{
			"player_stats": player_stats.to_dict(),
			"game_state": game_state.to_dict()
		}
	}
	with open(file_location, "w") as f:
		f.write(json.dumps(save_dict))

def load_game(file_location: str, player_stats: PlayerStats, game_state: GameState, player_sprite: PlayerSprite):
	save_dict = {}
	with open(file_location) as f:
		json_content = f.read()
		save_dict = json.loads(json_content)
	
	if any([key not in save_dict for key in ("save_version", "save_data")]) \
			or any([key not in save_dict["save_data"] for key in ("player_stats", "game_state")]):
		raise ValueError("Unable to load save game.")
	if save_dict["save_version"] != SAVE_VERSION:
		raise ValueError("Unabale to load different version of save game")
	
	player_stats.load_dict(save_dict["save_data"]["player_stats"])

	game_state.load_dict(save_dict["save_data"]["game_state"])

	player_sprite.breakable_group = game_state.block_group

def clamp(val: int | float, min_val: int | float, max_val: int | float) -> int | float:
	return min(max(val, min_val), max_val)

def extract_number_sign(value: int | float):
	if value == 0: 
		return 0
	return 1 if value > 0 else -1

def in_range(value: int | float, min_val: int | float, max_val: int | float) -> bool:
	return (min_val < value < max_val)

def random_with_rate(rates: list[float] | tuple[float, ...], rng: r.Random | None = None) -> int:
	temp_random = r.random() if rng == None else rng.random()
	length = len(rates)
	combined_weight = 0
	for i in range(length):
		current_weight = rates[i]
		if round(combined_weight + current_weight, 6) > temp_random:
			return i
		combined_weight = round(combined_weight + current_weight, 6)

	return -1

def load_picture(file: str, is_transparent: bool):
	if is_transparent:
		return pygame.image.load(file).convert_alpha()
	else:
		return pygame.image.load(file).convert()

def get_spritesheet_data(target_file: str, name: str) -> tuple[tuple[int, int], tuple[int, int]]:
	with open(target_file, "r") as f:
		for line in f:
			line = line.strip()
			if line != "" and line[0] == "#":
				continue
			key = line.split()
			if len(key) != 5:
				continue
			if key[0] == name:
				return((int(key[1]), int(key[2])), (int(key[3]), int(key[4])))
	raise ValueError("Name not found from targeted file.")

def get_surface_from_sprite_sheet(sprite_sheet_surface: pygame.Surface, index: tuple[int, int], size_per_image: tuple[int, int], scale: float | int, is_transparent: bool):
	width, height = size_per_image
	if is_transparent:
		image = pygame.Surface(size_per_image, pygame.SRCALPHA)
	else:
		image = pygame.Surface(size_per_image)
	image.blit(sprite_sheet_surface, (0,0), ((index[0] * width, index[1] * height), size_per_image))
	image = scale_surface(image, scale)
	return image

def get_surface_from_sprite_sheet2(sprite_sheet_surface: pygame.Surface, start_point: tuple[int, int], size_per_image: tuple[int, int], scale: float | int, is_transparent: bool):
	if is_transparent:
		image = pygame.Surface(size_per_image, pygame.SRCALPHA)
	else:
		image = pygame.Surface(size_per_image)
	image.blit(sprite_sheet_surface, (0,0), (start_point ,size_per_image))
	image = scale_surface(image, scale)
	return image

def check_initialization(obj: object, required_attrs: list[str]):
	uninitialized = [attr for attr in required_attrs if getattr(obj, attr) in (-1, -1.0, None)]
	if any(uninitialized):
		raise ValueError(f"Object are not initialized properly. Attributes that are not initialized: {uninitialized}.")

def scale_surface(surface: pygame.Surface, scale: float):
	width, height = surface.get_rect().size
	return pygame.transform.scale(surface, (round(width * scale), round(height * scale)))

if __name__ == "__main__":
	raise RuntimeError("This file cannot be execute directly. This file only work when imported.")