from settings import *
from player import Player
from sprites import *
from pytmx.util_pygame import load_pygame
from groups import AllSprites
#Mapeditor.org to make tiled maps

from random import randint, choice

class Game:
    def __init__(self):
        #Setup
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Not vampire survivors")
        self.clock = pygame.time.Clock()
        self.running = True

        #Groups
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        self.bullet_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()

        #Gun timer
        self.can_shoot = True
        self.shoot_time = 0
        self.gun_cooldown = 200

        #Audio
        self.shoot_sound = pygame.mixer.Sound(join("Vampire survivors", "audio", "shoot.wav"))
        self.shoot_sound.set_volume(0.4)
        self.impact_sound = pygame.mixer.Sound(join("Vampire survivors", "audio", "impact.ogg"))
        self.music = pygame.mixer.Sound(join("Vampire survivors", "audio", "music.wav"))
        self.music.set_volume(0.3)
        self.music.play(loops = -1)

        #Enemy spawn timer
        self.enemy_event = pygame.event.custom_type()
        pygame.time.set_timer(self.enemy_event, 150)
        self.spawn_positions = []
        self.load_images()
        self.setup()

    #Bullet and enemy images load here
    def load_images(self):
        self.bullet_surface = pygame.image.load(join("images", "gun", "bullet.png")).convert_alpha()

        folders = list(walk(join("images", "enemies")))[0][1] #Gets first item from those folders, which is name of folder and subfolders
        self.enemy_frames = {}
        for folder in folders:
            for folder_path, _, file_names in walk(join("images", "enemies", folder)):
                self.enemy_frames[folder] = [] #Makes a key of folder and value of empty list
                for file_name in sorted(file_names, key = lambda name: int(name.split(".")[0])):
                    full_path = join(folder_path, file_name)
                    surf = pygame.image.load(full_path).convert_alpha()
                    self.enemy_frames[folder].append(surf)


    def input(self):
        #Creates a bullet
        if pygame.mouse.get_pressed()[0] and self.can_shoot: #Checks for lmb
            self.shoot_sound.play()
            pos = self.gun.rect.center + self.gun.player_direction * 50 #Adds offset so it doesnt go on top of the gun, it goes out the end of it
            Bullet(self.bullet_surface, pos, self.gun.player_direction, (self.all_sprites, self.bullet_sprites))
            self.can_shoot = False
            self.shoot_time = pygame.time.get_ticks()

    def bullet_collision(self):
        if self.bullet_sprites:
            for bullet in self.bullet_sprites:
                self.collision_sprites = pygame.sprite.spritecollide(bullet, self.enemy_sprites, False, pygame.sprite.collide_mask) #Mask doesnt make much of a difference
                if self.collision_sprites:
                    self.impact_sound.play()
                    for sprite in self.collision_sprites:
                        sprite.destroy()
                    bullet.kill()

    def player_collision(self):
        if pygame.sprite.spritecollide(self.player, self.enemy_sprites, False, pygame.sprite.collide_mask): #Collide mask is very important for this for accurate hitbox
            self.running = False


    def run(self):
        while self.running:
            #Dt
            dt = self.clock.tick() / 1000

            #Event loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == self.enemy_event:
                    Enemy(choice(self.spawn_positions), choice(list(self.enemy_frames.values())), (self.all_sprites, self.enemy_sprites), self.player, self.collision_sprites)#Needs to be list or choice doesnt work

            #Update game
            self.gun_timer()
            self.input()
            self.all_sprites.update(dt)
            #You could combine both of these
            self.bullet_collision()
            self.player_collision()

            #Draw
            self.display_surface.fill("black")
            self.all_sprites.draw(self.player.rect.center) #Makes camera follow player
            pygame.display.update() #You can use flip if you want but im familiar with update

    #Checks if gun can shoot
    def gun_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.shoot_time >= self.gun_cooldown: #Checks if still on cd or not
                self.can_shoot = True

    def setup(self):
        map = load_pygame(join("Vampire survivors","data", "maps", "world.tmx"))

        for x, y, image in map.get_layer_by_name("Ground").tiles(): #Returning tiles and making them more accesible
            #Regular x and y are pixel size, but I need tile size for mapping
            Sprite((x * TILE_SIZE, y * TILE_SIZE), image, self.all_sprites)

        for obj in map.get_layer_by_name("Objects"): #Find the name in the website
            CollisionSprite((obj.x, obj.y), obj.image, (self.all_sprites, self.collision_sprites))

        #This can go anywhere since it's not meant to be visible
        for obj in map.get_layer_by_name("Collisions"):
            CollisionSprite((obj.x, obj.y), pygame.Surface((obj.width, obj.height)), self.collision_sprites) #Creates a rectangle for the hitbox of the terrain

        for obj in map.get_layer_by_name("Entities"):
            if obj.name == "Player":
                self.player = Player((obj.x, obj.y), self.all_sprites, self.collision_sprites) #Player himself isn't in collision sprites, only has access to it
                self.gun = Gun(self.player, self.all_sprites)
            else:
                self.spawn_positions.append((obj.x, obj.y))




    pygame.quit()

if __name__ == "__main__": #Safeguard
    game = Game()
    game.run()
