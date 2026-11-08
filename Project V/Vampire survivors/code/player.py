from settings import *

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, collision_sprites):
        super().__init__(groups)
        self.load_images()
        self.state, self.frame_index = "down", 0
        self.image = pygame.image.load(join("images", "player", "down", "0.png")).convert_alpha()
        self.rect = self.image.get_frect(center = pos)
        self.hitbox_rect = self.rect.inflate(-60, -80) #Avoids using a mask, so less hardware intensive

        #Movement
        self.direction = pygame.Vector2()
        self.speed = 500
        self.collision_sprites = collision_sprites

    def load_images(self):
        #Dictionary to import all the animations for player walk
        self.frames = {
            "left" :[],
            "right" :[], 
            "up" :[], 
            "down" :[]
            }
        for state in self.frames.keys():
            for folder_path, sub_folders, file_names in walk(join("images", "player", state)):
                if file_names: #Ignores parent folder
                    for file_name in sorted(file_names, key = lambda name: int(name.split(".")[0])): #Make sure the files are sorted so it looks normal, seperate file name from ending
                        full_path = join(folder_path, file_name)
                        surf = pygame.image.load(full_path).convert_alpha()
                        self.frames[state].append(surf)
        print(self.frames)
            

    def input(self):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_RIGHT] or keys[pygame.K_d]) - int(keys[pygame.K_LEFT] or keys[pygame.K_a])
        self.direction.y= int(keys[pygame.K_DOWN] or keys[pygame.K_s]) - int(keys[pygame.K_UP] or keys[pygame.K_w])
        self.direction = self.direction.normalize() if self.direction else self.direction #Prevents diagnols being much faster

    def move(self, dt):
        self.hitbox_rect.x += self.direction.x * self.speed * dt
        self.collision("horizontal")
        self.hitbox_rect.y += self.direction.y * self.speed * dt
        self.collision("vertical")
        self.rect.center = self.hitbox_rect.center #Combines the hitbox and sprite

    def collision(self, direction):
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.hitbox_rect):
                #These check if player is colliding with object and fixes their positions
                if direction == "horizontal":
                    if self.direction.x > 0: self.hitbox_rect.right = sprite.rect.left
                    if self.direction.x < 0 : self.hitbox_rect.left = sprite.rect.right
                else:
                    if self.direction.y > 0: self.hitbox_rect.bottom = sprite.rect.top 
                    if self.direction.y < 0 : self.hitbox_rect.top = sprite.rect.bottom

    def animate(self, dt):
        #Get the state
        if self.direction.x != 0:
            self.state = "right" if self.direction.x > 0 else "left"
        if self.direction.y != 0:
            self.state = "down" if self.direction.y > 0 else "up"

        #The animation
        self.frame_index = self.frame_index + 5 * dt if self.direction else 0 #Keeps your character still if not moving
        self.image = self.frames[self.state][int(self.frame_index) % len(self.frames[self.state])]

    def update(self, dt):
        self.input()
        self.move(dt)
        self.animate(dt)