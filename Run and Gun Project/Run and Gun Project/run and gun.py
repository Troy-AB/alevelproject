import pygame
import random
import csv

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Run & Gun')

#set framerate of the game
clock = pygame.time.Clock()
FPS = 240

#define game variables
GRAVITY = 0.8
SCROLL_THRESHOLD = 200
ROWS = 16
COLUMS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = 21
screen_scroll = 0
bg_scroll = 0
MAX_LEVELS = 3
level = 1
start_game = False

#initiate character action status
moving_left = False
moving_right = False
shoot = False

#load tiles
img_list = []
for x in range(TILE_TYPES):
	img = pygame.image.load(f'img/tile/{x}.png')
	img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
	img_list.append(img)




#load images

#background
sunny_bcg = pygame.image.load('img/Background/sunny.png').convert_alpha()

#game elements
bullet_img = pygame.image.load('img/icons/bullet.png').convert_alpha() #bullet
med_img = pygame.image.load('img/icons/health_box.png').convert_alpha() #med
ammo_img = pygame.image.load('img/icons/ammo_box.png').convert_alpha() #ammo

item_boxes = {
	'Health'	: med_img,
	'Ammo'		: ammo_img,
}

#buttons
start_img = pygame.image.load('img/start_btn.png').convert_alpha()
exit_img = pygame.image.load('img/exit_btn.png').convert_alpha()
restart_img = pygame.image.load('img/restart_btn.png').convert_alpha()


#colours
BGC = (128, 128, 128)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED =  (255, 0, 0)
GREEN = (0, 255, 0)

#fonts
font = pygame.font.SysFont('Arial', 30)

def draw_text(text, font, text_color, x_pos, y_pos):
	img = font.render(text, True, text_color)
	screen.blit(img, (x_pos, y_pos))


def draw_background():
	screen.fill(BGC)
	screen.blit(sunny_bcg, (0,0))

#reset level
def reset():
	enemy_group.empty()
	bullet_group.empty()
	item_box_group.empty()
	decoration_group.empty()
	water_group.empty()
	exit_group.empty()

	#create empty tile list
	data = []
	for row in range(ROWS):
		r = [-1] * COLUMS
		data.append(r)

	return data

	

#character class
class character(pygame.sprite.Sprite):
	def __init__(self,type, x_coordinate, y_coordinate, scale, speed, ammo):
		self.alive = True #check if i need this later
		self.type = type
		self.speed = speed
		self.ammo = ammo
		self.start_ammo = ammo
		self.health = 100
		self.max_health = self.health
		self.shoot_cooldown = 0
		self.direction = 1
		self.y_velocity = 0
		self.jump = False
		self.flip = False
		self.update_time = pygame.time.get_ticks()
		
		

		#enemy variables
		self.move_counter = 0
		self.vision = pygame.Rect(0, 0, 150, 20)
		self.idle = False
		self.idle_counter = 0

		#load the character sprite and assign it to a rect
		pygame.sprite.Sprite.__init__(self)
		img = pygame.image.load(f'img/{self.type}/idle/0.png').convert_alpha()
		self.image = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)) )
		self.rect = self.image.get_rect() #adds a rect to the image which can be controlled
		self.rect.center = (x_coordinate, y_coordinate)

		self.width = self.image.get_width()
		self.height = self.image.get_height()

	def update(self):
		self.check_alive()
		#update cooldown
		if self.shoot_cooldown > 0:
			self.shoot_cooldown -= 1	

	#method to allow the character to move
	def move(self, moving_left, moving_right):
		
		#set movement values to zero
		screen_scroll = 0
		dx = 0
		dy = 0

		#assign magnitude of speed
		if moving_left == True:
			dx = -self.speed
			self.flip = True
			self.direction = -1
		if moving_right == True:	
			dx = self.speed
			self.flip = False
			self.direction = 1

		#jump
		if self.jump == True:
			self.y_velocity = -15
			self.jump = False
		
		#apply gravity
		self.y_velocity += GRAVITY
		if self.y_velocity > 10:
			y_velocity = 10
		dy += self.y_velocity

		#check for collision
		for tile in world.obstacle_list:
			#check collision in the x direction
			if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
				dx = 0
			#check for collision in the y direction
			if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
				#check if below the ground, i.e. jumping
				if self.y_velocity < 0:
					self.y_velocity = 0
					dy = tile[1].bottom - self.rect.top
				#check if above the ground, i.e. falling
				elif self.y_velocity >= 0:
					self.y_velocity = 0
					self.in_air = False
					dy = tile[1].top - self.rect.bottom

		#check for water contact
		if pygame.sprite.spritecollide(self, water_group, False):
			self.health = 0

		#check for contact with exit
		level_finish = False
		if pygame.sprite.spritecollide(self, exit_group, False):
			level_finish = True

		#check if fell off map
		if self.rect.bottom > SCREEN_HEIGHT:
			self.health = 0			

		#check if near world edge
		if self.type == 'player':
			if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
				dx = 0

		#update rect pos
		self.rect.x += dx
		self.rect.y += dy

		#update scroll
		if self.type == 'player':
			if (self.rect.right > SCREEN_WIDTH - SCROLL_THRESHOLD and bg_scroll < (world.level_length * TILE_SIZE) - SCREEN_WIDTH)\
				  or (self.rect.left < SCROLL_THRESHOLD and bg_scroll > abs(dx)):
				self.rect.x -= dx
				screen_scroll = -dx

			return screen_scroll, level_finish

	#shoot method
	def shoot(self):
		if self.shoot_cooldown == 0 and self.ammo > 0:
			self.shoot_cooldown = 20
			bullet = Bullet(self.rect.centerx + (0.6 * self.rect.size[0] * self.direction),
					self.rect.centery + (0.25 *self.rect.size[1]), self.direction)
			bullet_group.add(bullet)
		#subtract ammo each time player shoots
		self.ammo -= 1

	#give the enemy AI
	def AI(self):
		if self.idle ==False and random.randint(1, 200) == 5:
			self.idle = True
			self.idle_counter = 50

		#check if player is near enemy
		if self.vision.colliderect(player.rect):
			self.speed = 0
			self.shoot()
		
		if self.alive and player.alive:
			if self.idle == False:
				if self.direction == 1:
					ai_right = True
				else:
					ai_right = False
				ai_left = not ai_right
				self.move(ai_left, ai_right)
				self.move_counter += 1

				#update the vision area of enemy with movement
				self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)
				#make rectanlge visible
				###pygame.draw.rect(screen, RED, self.vision)


				if self.move_counter > TILE_SIZE:
					self.direction *= -1
					self.move_counter *= -1
		else:
			self.idle_counter -= 1
			if self.idle_counter <= 0:
				self.idle = False
				self.speed = 5

		#scroll
		self.rect.x += screen_scroll
		
	#check if character is alive
	def check_alive(self) :
		if self.health <= 0 and self.alive:
			self.health = 0
			self.speed = 0
			self.alive = False

			#change sprite
			print("Changing image to death image")    
			self.image = pygame.image.load('img/player/Death/0.png')
			old_rect = self.rect
			self.rect = self.image.get_rect()
			self.rect.topleft = old_rect.topleft

	#draw method for character
	def draw(self):
		screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)

#create world and load data
class World():
	def __init__(self):
		self.obstacle_list = []

	def process_data(self, data):
		self.level_length = len(data[0])
		#iterate through each value in level data file
		for y, row in enumerate(data):
			for x, tile in enumerate(row):
				if tile >= 0:
					img = img_list[tile]
					img_rect = img.get_rect()
					img_rect.x = x * TILE_SIZE
					img_rect.y = y * TILE_SIZE
					tile_data = (img, img_rect)
					if tile >= 0 and tile <= 8:
						self.obstacle_list.append(tile_data)
					elif tile >= 9 and tile <= 10:
						water = Water(img, x * TILE_SIZE, y * TILE_SIZE)
						water_group.add(water)
					elif tile >= 11 and tile <= 14:
						decoration = Decoration(img, x * TILE_SIZE, y * TILE_SIZE)
						decoration_group.add(decoration)
					elif tile == 15:#create player
						player = character("player", x*TILE_SIZE, y*TILE_SIZE, 0.05, 5, 20)
						health_bar = HealthBar(10, 10, player.health, player.health)
					elif tile == 16:#create enemies
						enemy = character("enemy", x*TILE_SIZE, y*TILE_SIZE, 0.05, 5, 2000)
						enemy_group.add(enemy)
					elif tile == 17:#create ammo box
						item_box = ItemBox('Ammo', x * TILE_SIZE, y * TILE_SIZE)
						item_box_group.add(item_box)
					elif tile == 18:#create ammo
						item_box = ItemBox('Ammo', x * TILE_SIZE, y * TILE_SIZE)
						item_box_group.add(item_box)
					elif tile == 19:#create health box
						item_box = ItemBox('Health', x * TILE_SIZE, y * TILE_SIZE)
						item_box_group.add(item_box)
					elif tile == 20:#create exit
						exit = Exit(img, x * TILE_SIZE, y * TILE_SIZE)
						exit_group.add(exit)

		return player, health_bar


	def draw(self):
		for tile in self.obstacle_list:
			tile[1][0] += screen_scroll
			screen.blit(tile[0], tile[1])

#random world decor
class Decoration(pygame.sprite.Sprite):
	def __init__(self, img, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = img
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

	def update(self):
		self.rect.x += screen_scroll

#water
class Water(pygame.sprite.Sprite):
	def __init__(self, img, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = img
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

	def update(self):
		self.rect.x += screen_scroll

#exit to next level
class Exit(pygame.sprite.Sprite):
	def __init__(self, img, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = img
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

	def update(self):
		self.rect.x += screen_scroll

#item box class
class ItemBox(pygame.sprite.Sprite):
	def __init__ (self, item_type,  x_pos, y_pos):
		pygame.sprite.Sprite.__init__(self)
		self.item_type = item_type
		self.image = item_boxes[self.item_type]
		self.rect = self.image.get_rect()
		self.rect.midtop = (x_pos + TILE_SIZE // 2, y_pos + (TILE_SIZE - self.image.get_height()))

	def update(self):
		#scroll
		self.rect.x += screen_scroll

		#check if box collected
		if pygame.sprite.collide_rect(self, player):
			#act depending on what item box has been picked up
			if self.item_type == 'Health':
				player.health += 25
				if player.health > player.max_health:
					player.health = player.max_health
			elif self.item_type == 'Ammo':
				player.ammo += 10
			#and delete item box
			self.kill()

#healthbar class
class HealthBar():
	def __init__(self, x, y, health, max_health):
		self.x = x
		self.y = y
		self.health = health
		self.max_health = max_health

	def draw(self, health):
		#refresh current health
		self.health = health
		#display health proportionately
		ratio = self.health / self.max_health
		pygame.draw.rect(screen, BLACK, (self.x - 2, self.y - 2, 154, 24))
		pygame.draw.rect(screen, RED, (self.x, self.y, 150, 20))
		pygame.draw.rect(screen, GREEN, (self.x, self.y, 150 * ratio, 20))

#bullet class
class Bullet(pygame.sprite.Sprite):
	def __init__ (self, x_pos, y_pos, direction):
		pygame.sprite.Sprite.__init__(self)
		self.speed = 10
		self.image = bullet_img
		self.rect = self.image.get_rect()
		self.rect.center = (x_pos, y_pos)
		self.direction = direction

	def update(self):
		#move bullet
		self.rect.x += (self.direction * self.speed) #+screen_scroll

		#delete offscreen bullets
		if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
			self.kill()

		#block collision check
		for tile in world.obstacle_list:
			if tile[1].colliderect(self.rect):
				self.kill()

		#enemy collision check
		if pygame.sprite.spritecollide(player, bullet_group, False):
			if player.alive:
				self.kill()
				player.health -= 5
		if pygame.sprite.spritecollide(enemy, bullet_group, False):
			if enemy.alive:
				self.kill()
				enemy.health -= 25
				#print(enemy.health)

#button class
class Button():
	def __init__(self,x, y, image, scale):
		width = image.get_width()
		height = image.get_height()
		self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
		self.rect = self.image.get_rect()
		self.rect.topleft = (x, y)
		self.clicked = False

	def draw(self, surface):
		action = False

		#get mouse position
		pos = pygame.mouse.get_pos()

		#check mouseover and clicked conditions
		if self.rect.collidepoint(pos):
			if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
				action = True
				self.clicked = True

		if pygame.mouse.get_pressed()[0] == 0:
			self.clicked = False

		#draw button
		surface.blit(self.image, (self.rect.x, self.rect.y))

		return action



#create buttons
start_button = Button(SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT // 2 - 150, start_img, 1 )
exit_button = Button(SCREEN_WIDTH // 2 - 110, SCREEN_HEIGHT // 2 + 50, exit_img, 1 )
restart_button = Button(SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT // 2 - 150, restart_img, 2 )

#create sprite groups
enemy_group = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()

#load characters
player = character("player", 500,500, 0.05, 100, 20000000)
health_bar = HealthBar(10, 10, player.health, player.health)

enemy = character("enemy", 500,400, 0.05, 5, 2000)
enemy_group.add(enemy)


##LOAD THE WORLD##

#create empty list to load tile data
world_data = []
for row in range(ROWS):
	r = [-1] * COLUMS
	world_data.append(r)
#load in level data and load
with open(f'level{level}_data.csv', newline='') as csvfile:
	reader = csv.reader(csvfile, delimiter=',')
	for x, row in enumerate(reader):
		for y, tile in enumerate(row):
			world_data[x][y] = int(tile)
world = World()
player, health_bar = world.process_data(world_data)



run = True
while run:
    
	clock.tick(FPS)

	if start_game == False:
		#bring up main menu
		screen.blit(sunny_bcg, (0,0))
		#load buttons
		if start_button.draw(screen):
			start_game = True
		elif exit_button.draw(screen):
			run = False
	else: 

		#update background
		draw_background()
		#draw world map
		world.draw()

		draw_text(f'Ammo: {player.ammo}', font, WHITE, 10, 35 )

		#show player health
		health_bar.draw(player.health)

		player.update()
		player.draw()
		enemy.update()

		

		screen_scroll, level_finish = player.move(moving_left, moving_right)
	
		#update enemies
		for enemy in enemy_group:
			enemy.AI()
			enemy.update()
			enemy.draw()

		#update and draw sprite groups
		bullet_group.update()
		bullet_group.draw(screen)

		item_box_group.update()
		item_box_group.draw(screen)

		decoration_group.update()
		decoration_group.draw(screen)

		water_group.update()
		water_group.draw(screen)

		exit_group.update()
		exit_group.draw(screen)

		#update player actions
		if player.alive:
			#shoot
			if shoot:
				player.shoot()
			if level_finish:
				level += 1 
				if level <= MAX_LEVELS:
					with open(f'level{level}_data.csv', newline='') as csvfile:
						reader = csv.reader(csvfile, delimiter=',')
						for x, row in enumerate(reader):
							for y, tile in enumerate(row):
								world_data[x][y] = int(tile)
						world = World()
						player, health_bar = world.process_data(world_data)


		else:
			screen_scroll = 0
			if restart_button.draw(screen):
				bg_scroll = 0
				world_data = reset()
				#load in level data and create world
				with open(f'level{level}_data.csv', newline='') as csvfile:
					reader = csv.reader(csvfile, delimiter=',')
					for x, row in enumerate(reader):
						for y, tile in enumerate(row):
							world_data[x][y] = int(tile)
				world = World()
				player, health_bar = world.process_data(world_data)






	#event handler
	for event in pygame.event.get():
		#quit the game
		if event.type == pygame.QUIT:
			run = False

		#keyboard pressed down	
		if event.type == pygame.KEYDOWN:
			#move left
			if event.key == pygame.K_a or event.key == pygame.K_LEFT:
				moving_left = True
			#move right
			if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
				moving_right = True
			#shoot
			if event.key == pygame.K_SPACE:
				shoot = True
			#jump
			if  event.key == pygame.K_w and player.alive == True:
				player.jump = True
		
		#keyboard button released
		if event.type == pygame.KEYUP:
			if event.key == pygame.K_a or event.key == pygame.K_LEFT:
				moving_left = False
			if event.key == pygame.K_d or pygame.K_RIGHT:
				moving_right = False
			if event.key == pygame.K_SPACE:
				shoot = False



	pygame.display.update()

pygame.quit()



