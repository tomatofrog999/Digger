import pygame
import random as r
from enum import Enum

class BlockSprite(pygame.sprite.Sprite):
	def __init__(self, surface: pygame.Surface, topleft: tuple[int, int], max_health: float, flip_x: bool, flip_y: bool, is_bomb: bool, bomb_damage: int):
		super().__init__()
		surface = pygame.transform.flip(surface, flip_x, flip_y)

		self.image = surface
		
		self.rect = self.image.get_rect()
		self.rect.topleft = topleft

		self.max_health = max_health
		self.is_bomb = is_bomb
		self.bomb_damage = bomb_damage

		self.damage_taken = 0.0

	def destroy(self, player: Player):
		super().kill()
		if self.is_bomb:
			player.remove_health(self.bomb_damage)

	def get_rect(self) -> pygame.Rect:
		if not isinstance(self.rect, pygame.Rect):
			raise TypeError("'rect' variable need to be pygame.Rect type.")
		return self.rect

class Player(pygame.sprite.Sprite):
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

	def __init__(self, topleft: tuple[float, float], hitblock_size: tuple[int, int]):
		super().__init__()
		self.walk_acceleration = -1.0
		self.slow_down_acceleration = -1.0
		self.max_walk_speed = -1.0
	
		self.max_side_speed = -1.0
		self.max_down_speed = -1.0
		self.max_up_speed = -1.0
	
		self.gravity = -1
	
		self.jump_speed = -1.0
		self.wall_kick_speed = -1.0
		self.wall_slide_acceleration = -1.0
		self.wall_slide_speed_threshold = -1.0
		self.tick_till_enable_slide = -1
	
		self.break_block_distance = -1
		self.addition_speed_when_break_block = -1.0
		self.block_width = -1
		self.block_height = -1
	
		self.origin_break_block_point_x = -1
		self.origin_break_block_point_y = -1
	
		self.image_offset: tuple[int, int] = (0,0)
	
		self.animation_dict: dict[Player.AnimationState, Player.AnimationData] | None = None
		self.last_action: Player.AnimationState = Player.AnimationState.IDLE
		self.action: Player.AnimationState = Player.AnimationState.IDLE
		self.update_animation_time = 0
		self.animation_frame = 0
		self.breakable_group: pygame.sprite.Group[BlockSprite] | None = None
		self.screen: pygame.Surface | None = None
	
		self.max_health = -1
		self.health = -1
		self.max_energy = -1
		self.energy = -1
	
		self.touch_wall_side = Player.TouchWallState.NOT_TOUCH_WALL
		self.facing_left = False # For movement and surface mirroring
		self.facing_direction = Player.DirectionState.DOWN # For diging direction
		self.break_damage = -1.0
		self.break_damage_modifier = -1.0
		self.on_beat_extra_damage = -1.0
		self.on_beat_extra_damage_modifier = -1.0
		self.on_beat_hit = False
	
		self.airtime_tick = 0
		self.touch_wall_tick = 0
	
		self.velocity_x = 0.0
		self.velocity_y = 0.0
		self.game_over = False

		self.rect = pygame.FRect(topleft, hitblock_size)

	def check_init(self):
		required_attrs = [
			'walk_acceleration', 'slow_down_acceleration', 'max_walk_speed',
			'max_side_speed', 'max_down_speed', 'max_up_speed', 'jump_speed',
			'wall_kick_speed', 'wall_slide_acceleration', 'wall_slide_speed_threshold',
			'tick_till_enable_slide', 'break_block_distance', 'addition_speed_when_break_block',
			'block_width', 'block_height', 'origin_break_block_point_x', 'origin_break_block_point_y',
			'animation_dict', 'breakable_group', 'screen',
			'max_health', 'health', 'max_energy', 'energy',
			'break_damage', 'break_damage_modifier', 'gravity',
			'on_beat_extra_damage', 'on_beat_extra_damage_modifier'
		]
		check_initialization(self, required_attrs)

	def init_gravity_constant(self, gravity: float):
		self.gravity = gravity
		return self

	def init_walk_constant(self, walk_acceleration: float, slow_down_acceleration: float, max_walk_speed: float):
		self.walk_acceleration = walk_acceleration
		self.slow_down_acceleration = slow_down_acceleration
		self.max_walk_speed = max_walk_speed
		return self

	def init_max_speed_constant(self, max_side_speed: float, max_down_speed: float, max_up_speed: float):
		self.max_side_speed = max_side_speed
		self.max_down_speed = max_down_speed
		self.max_up_speed = max_up_speed
		return self

	def init_jump_slide_constant(self, jump_speed: float, wall_kick_speed: float, wall_slide_acceleration: float, wall_slide_speed_threshold: float, tick_till_enable_slide: int):
		self.jump_speed = jump_speed
		self.wall_kick_speed = wall_kick_speed
		self.wall_slide_acceleration = wall_slide_acceleration
		self.wall_slide_speed_threshold = wall_slide_speed_threshold
		self.tick_till_enable_slide = tick_till_enable_slide
		return self

	def init_digging_constant(self, break_block_distance: int, addition_speed_when_break_block: float, block_width: int, block_height: int):
		self.break_block_distance = break_block_distance
		self.addition_speed_when_break_block = addition_speed_when_break_block
		self.block_width = block_width
		self.block_height = block_height
		self.origin_break_block_point_x = self.block_width// 2 + self.get_rect().width // 2
		self.origin_break_block_point_y = self.block_height // 2 + self.get_rect().height // 2
		return self

	def init_break_damage_constant(self, break_damage: float, break_damage_modifier: float):
		self.break_damage = break_damage
		self.break_damage_modifier = break_damage_modifier
		return self
	
	def init_animation_data(self, animation_data: dict[AnimationState, AnimationData]):
		self.animation_dict = animation_data
		if Player.AnimationState.IDLE not in animation_data:
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

	def init_health(self, max_health: int):
		self.max_health = max_health
		self.health = max_health
		return self
	
	def init_energy(self, energy: int):
		self.max_energy = energy
		self.energy = energy
		return self

	def init_on_beat_constant(self, on_beat_extra_damage: float, on_beat_extra_damage_modifier: float):
		self.on_beat_extra_damage = on_beat_extra_damage
		self.on_beat_extra_damage_modifier = on_beat_extra_damage_modifier
		return self

	def get_rect(self) -> pygame.FRect:
		if not isinstance(self.rect, pygame.FRect):
			raise TypeError("'rect' variable need to be pygame.FRect type.")
		return self.rect

	def get_animation_dict(self) -> dict[AnimationState, AnimationData]:
		if not isinstance(self.animation_dict, dict):
			raise TypeError("'animation_data' variable need to be dict type.")
		return self.animation_dict

	def get_animation_data(self, state: AnimationState) -> Player.AnimationData:
		animation_dict = self.get_animation_dict()
		if not state in animation_dict:
			return animation_dict[Player.AnimationState.IDLE]
		return animation_dict[state]

	def set_surface(self, animation_surface: pygame.Surface, size_per_image: tuple[int, int], surface_scale: int):
		for animation in self.get_animation_dict().values():
			temp_list = []
			for i in range(animation.start_index, animation.start_index + animation.step):
				temp_list.append(get_surface_from_sprite_sheet(animation_surface, (i, 0), size_per_image, surface_scale, True))
			animation.surfaces = tuple(temp_list)
		default_animation = self.get_animation_data(Player.AnimationState.IDLE)
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
					self.change_action(Player.AnimationState.IDLE, forced=True)
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
				temp_velocity = -self.walk_acceleration * delta_time
				temp_velocity = clamp(-self.max_walk_speed - self.velocity_x, temp_velocity, 0)
			else:
				self.facing_left = False
				temp_velocity = self.walk_acceleration * delta_time
				temp_velocity = clamp(self.max_walk_speed - self.velocity_x, 0, temp_velocity)
			self.velocity_x += temp_velocity

			self.change_action(Player.AnimationState.WALK)
		elif self.velocity_x != 0:
			self.velocity_x -= extract_number_sign(self.velocity_x) * min(abs(self.velocity_x), self.slow_down_acceleration * delta_time)
		else:
			self.change_action(Player.AnimationState.IDLE)
		self.velocity_x = clamp(self.velocity_x, -self.max_side_speed, self.max_side_speed)
	
		can_wall_sliding = self.touch_wall_tick >= self.tick_till_enable_slide and self.airtime_tick > self.tick_till_enable_slide
		if space_pressed and (self.airtime_tick <= 0 or can_wall_sliding) and not (j_pressed or k_pressed):
			if can_wall_sliding and self.touch_wall_side != Player.TouchWallState.NOT_TOUCH_WALL:
				if self.touch_wall_side == Player.TouchWallState.TOUCH_WALL_LEFT:
					self.velocity_x += self.wall_kick_speed
				else:
					self.velocity_x -= self.wall_kick_speed
				self.touch_wall_tick = 0
				self.change_action(Player.AnimationState.WALL_JUMP)
			else:
				self.change_action(Player.AnimationState.JUMP)
			self.velocity_y -= self.jump_speed
	
		if can_wall_sliding and self.velocity_y > self.wall_slide_speed_threshold:
			self.velocity_y -= self.wall_slide_acceleration * delta_time
		if can_wall_sliding:
			self.change_action(Player.AnimationState.WALL_SLIDE)
		elif self.action == Player.AnimationState.WALL_SLIDE and not can_wall_sliding:
			self.change_action(Player.AnimationState.IDLE, forced=True)
	
		self.velocity_y += self.gravity * delta_time
		self.velocity_y = clamp(self.velocity_y, -self.max_up_speed, self.max_down_speed)

	def update_position_and_collision(self, delta_time: float):
		self.touch_wall_side = Player.TouchWallState.NOT_TOUCH_WALL
		srect = self.get_rect()
		srect.x += self.velocity_x * delta_time
		if self.velocity_x != 0:
			for block in self.breakable_group or ():
				if srect.colliderect(block.get_rect()):
					if self.velocity_x > 0:
						srect.right = block.get_rect().left
						self.touch_wall_side = Player.TouchWallState.TOUCH_WALL_RIGHT
					else:
						srect.left = block.get_rect().right
						self.touch_wall_side = Player.TouchWallState.TOUCH_WALL_LEFT
					self.velocity_x = 0
					break
		if self.touch_wall_side == Player.TouchWallState.NOT_TOUCH_WALL:
			self.touch_wall_tick = 0
		else:
			self.touch_wall_tick += 1
	
		srect.y += self.velocity_y * delta_time
		self.touch_ground = False
		if self.velocity_y != 0:
			for block in self.breakable_group or ():
				if srect.colliderect(block.get_rect()):
					if self.velocity_y > 0:
						srect.bottom = block.get_rect().top
						self.touch_ground = True
						self.airtime_tick = 0
						if self.action in (Player.AnimationState.JUMP, Player.AnimationState.FALL, Player.AnimationState.WALL_SLIDE):
							self.change_action(Player.AnimationState.IDLE, forced=True)
					else:
						srect.top = block.get_rect().bottom
					self.velocity_y = 0
					break
		if not self.touch_ground:
			self.airtime_tick += 1
			self.change_action(Player.AnimationState.FALL)

	def handle_break_block(self, keys: pygame.key.ScancodeWrapper, events: list[pygame.Event]):
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
					self.facing_direction = Player.DirectionState.UP
				elif s_pressed:
					self.facing_direction = Player.DirectionState.DOWN

			if not (a_pressed and d_pressed):
				if a_pressed:
					self.facing_direction = Player.DirectionState.LEFT
				elif d_pressed:
					self.facing_direction = Player.DirectionState.RIGHT

		if (j_pressed or k_pressed) and not_diagonally:
			digging_offset_x = 0
			digging_offset_y = 0
			if w_pressed or s_pressed or a_pressed or d_pressed:
				if w_pressed:
					digging_offset_y -= self.origin_break_block_point_y
					self.facing_direction = Player.DirectionState.UP
				if s_pressed:
					digging_offset_y += self.origin_break_block_point_y
					self.facing_direction = Player.DirectionState.DOWN
			
				if a_pressed:
					digging_offset_x -= self.origin_break_block_point_x
					self.facing_direction = Player.DirectionState.LEFT
				if d_pressed:
					digging_offset_x += self.origin_break_block_point_x
					self.facing_direction = Player.DirectionState.RIGHT
			else:
				if self.facing_direction == Player.DirectionState.UP:
					digging_offset_y -= self.origin_break_block_point_y
				elif self.facing_direction == Player.DirectionState.DOWN:
					digging_offset_y += self.origin_break_block_point_y

				elif self.facing_direction == Player.DirectionState.LEFT:
					digging_offset_x -= self.origin_break_block_point_x
				elif self.facing_direction == Player.DirectionState.RIGHT:
					digging_offset_x += self.origin_break_block_point_x
	
			is_collide = False
			srect = self.get_rect()
			for _ in range(self.break_block_distance):
				for block in self.breakable_group or ():
					is_collide = block.get_rect().collidepoint((srect.centerx + digging_offset_x, srect.centery + digging_offset_y))
					if is_collide:
						self.change_action(Player.AnimationState.DIG)
						if self.on_beat_hit:
							block.damage_taken += (self.break_damage + self.on_beat_extra_damage) * (self.break_damage_modifier + self.on_beat_extra_damage_modifier)
						else:
							block.damage_taken += self.break_damage * self.break_damage_modifier
						
						if block.damage_taken >= block.max_health:	
							if digging_offset_x != 0:
								self.velocity_x += extract_number_sign(digging_offset_x) * self.addition_speed_when_break_block
							if digging_offset_y > 0:
								self.velocity_y += self.addition_speed_when_break_block
							block.destroy(self)
						break
				if is_collide:
					break
				if digging_offset_x != 0 and digging_offset_y == 0:
					digging_offset_x += extract_number_sign(digging_offset_x) * self.block_width
				elif digging_offset_y != 0 and digging_offset_x == 0:
					digging_offset_y += extract_number_sign(digging_offset_y) * self.block_height

	def update(self, keys: pygame.key.ScancodeWrapper, events: list[pygame.Event], dt: float):
		self.handle_movement(keys, events, dt)
		self.update_position_and_collision(dt)
		self.handle_break_block(keys, events)
	
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
		

class BlockData:
	def __init__(self, surface: pygame.Surface, max_health: float, spawn_weight: float):
		self.surface = surface
		self.max_health = max_health
		self.spawn_weight = spawn_weight

class LayerData:
	def __init__(self, end_layer: int, block_tuple: tuple[BlockData, ...], bomb_rate: float, bomb_damage: int):
		self.end_layer = end_layer
		self.block_tuple = block_tuple
		self.bomb_rate = bomb_rate
		self.bomb_damage = bomb_damage
		combined_weight = 0
		for x in self.block_tuple:
			combined_weight += x.spawn_weight

		if round(combined_weight, 4) != 1.0:
			raise ValueError("Combined weight of BlockData in LayerData is not 1.")

	def get_random_block(self) -> BlockData:
		temp_random = r.random()
		length = len(self.block_tuple)
		combined_weight = 0
		for i in range(length):
			current_weight = self.block_tuple[i].spawn_weight
			if round(combined_weight + current_weight, 4) > temp_random:
				return self.block_tuple[i]
			combined_weight = round(combined_weight + current_weight, 4)

		raise RuntimeError(f"Impossible state on get_random_block.")

class MapData:
	def __init__(self, layer_tuple: tuple[LayerData, ...], block_width: int, block_height: int):
		self.layer_tuple = tuple(sorted(layer_tuple, key=(lambda x: x.end_layer)))
		self.block_width = block_width
		self.block_height = block_height

	def create_sprite_group(self, width: int, height: int, map_position: tuple[int, int]) -> pygame.sprite.Group[BlockSprite]:
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
				is_bomb = r.random() < layer.bomb_rate
				if is_bomb:
					bomb_block = pygame.Surface((self.block_width, self.block_height))
					bomb_block.fill("red")
					block = BlockSprite(bomb_block, (block_x + map_position[0], block_y + map_position[1]), 0, False, False, True, layer.bomb_damage)
				else:
					block = BlockSprite(block_data.surface, (block_x + map_position[0], block_y + map_position[1]), block_data.max_health, False, False, False, 0)
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

		self.music_file: str | None = None
		self.loudness = -1
		self.rhythm_index = 0
		self.wrong_press_next_reset = 0
		self.wrong_press_cooldown_ms = wrong_press_cooldown_ms
		self.current_music_time = 0
		self.screen: pygame.Surface | None = None
		self.line_offset_x = -1
		self.line_pos_ratio = -1.0
		self.topleft_pos = (0, 0)
		self.rhythm_show_length_ms = rhythm_show_length_ms

	def init_music(self, music_file: str, loudness: float):
		self.music_file = music_file
		self.loudness = loudness
		return self

	def init_screen(self, screen: pygame.Surface, line_pos_ratio: float, center_pos: tuple[int, int] = (0, 0)):
		self.screen = screen
		self.topleft_pos = (center_pos[0] - self.width // 2, center_pos[1] - self.height // 2)
		self.line_offset_x = self.width * line_pos_ratio
		self.line_pos_ratio = line_pos_ratio
		return self

	def check_init(self):
		required_attrs = [
			'music_file', 'loudness', 'screen', 'line_offset_x', 'line_pos_ratio'
		]
		check_initialization(self, required_attrs)

	def get_screen(self) -> pygame.Surface:
		if not isinstance(self.screen, pygame.Surface):
			raise TypeError("'screen' variable need to be pygame.Surface type.")
		return self.screen

	def start(self):
		if self.music_file == None:
			raise TypeError("'music_file' variable cannot be None type.")
		pygame.mixer.music.load(self.music_file)
		pygame.mixer.music.set_volume(self.loudness)
		pygame.mixer.music.play()

	def update(self, player: Player, pressed_dig: bool):
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

def clamp(val: int | float, min_val: int | float, max_val: int | float) -> int | float:
	return min(max(val, min_val), max_val)

def extract_number_sign(value: int | float):
	if value == 0: 
		return 0
	return 1 if value > 0 else -1

def in_range(value: int | float, min_val: int | float, max_val: int | float) -> bool:
	return (min_val < value < max_val)

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

def get_surface_from_sprite_sheet(sprite_sheet_surface: pygame.Surface, index: tuple[int, int], size_per_image: tuple[int, int], scale: int, is_transparent: bool):
	width, height = size_per_image
	if is_transparent:
		image = pygame.Surface(size_per_image, pygame.SRCALPHA)
	else:
		image = pygame.Surface(size_per_image)
	image.blit(sprite_sheet_surface, (0,0) ,((index[0] * width, index[1] * height) ,size_per_image))
	image = pygame.transform.scale(image, (width * scale, height * scale))
	return image

def get_surface_from_sprite_sheet2(sprite_sheet_surface: pygame.Surface, start_point: tuple[int, int], size_per_image: tuple[int, int], scale: int, is_transparent: bool):
	width, height = size_per_image
	if is_transparent:
		image = pygame.Surface(size_per_image, pygame.SRCALPHA)
	else:
		image = pygame.Surface(size_per_image)
	image.blit(sprite_sheet_surface, (0,0) ,(start_point ,size_per_image))
	image = pygame.transform.scale(image, (width * scale, height * scale))
	return image

def check_initialization(obj: object,required_attrs: list[str]):
	uninitialized = [attr for attr in required_attrs if getattr(obj, attr) in (-1, -1.0, None)]
	if any(uninitialized):
		raise ValueError(f"Object are not initialized properly. Attributes that are not initialized: {uninitialized}.")

if __name__ == "__main__":
	raise RuntimeError("This file cannot be execute directly. This file only work when imported.")