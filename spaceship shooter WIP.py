import pygame
from random import randint, uniform
from os.path import join

#Sprite classes
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.normal_image = pygame.image.load(r"C:\Users\sebas\Desktop\personal\5games-main\space shooter\images\player.png").convert_alpha()
        self.image = self.normal_image
        self.gray_image = pygame.transform.grayscale(self.normal_image) #Transform can lower quality, especially rotating, rotozoom is better for keeping quality. No universal better zoom, depends on scenario
        self.rect = self.image.get_frect(center=(600, 650))
        self.direction = pygame.math.Vector2(0, 0)
        self.speed = 300

        #Cd for laser
        self.can_shoot = True
        self.laser_shoot_time = 0
        self.cooldown_duration = 100

        #Mask
        self.mask = pygame.mask.from_surface(self.image)
        #mask_surf = mask.to_surface()
        #You can hide pixels for a flash effect
        #mask_surf.set_colorkey((0,0,0))


    def laser_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.laser_shoot_time >= self.cooldown_duration:
                self.can_shoot = True

    def update(self, dt):
        #Basic movement using arrow keys
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
        self.direction.y = int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])
        self.direction = self.direction.normalize() if self.direction else self.direction
        self.rect.center += self.direction * self.speed * dt

        #Keeps the player in the window
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WINDOW_WIDTH:
            self.rect.right = WINDOW_WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > WINDOW_HEIGHT:
            self.rect.bottom = WINDOW_HEIGHT

        current_center = self.rect.center
        if upgrades == 2:
            self.image = self.gray_image
        else:
            self.image = self.normal_image

        #Laser shooting
        recent_keys = pygame.key.get_just_pressed()
        if recent_keys[pygame.K_SPACE] and self.can_shoot:
            if upgrades == 1:
                Laser(laser_surf, self.rect.midtop, (all_sprites, laser_sprites))
            else:
                Laser(laser_surf, self.rect.midtop, (all_sprites, laser_sprites))
                Laser(laser_surf, self.rect.midleft, (all_sprites, laser_sprites))
                Laser(laser_surf, self.rect.midright, (all_sprites, laser_sprites))
            self.can_shoot = False
            self.laser_shoot_time = pygame.time.get_ticks()
            laser_sound.play()
        #Laser cd
        self.laser_timer()

class Star(pygame.sprite.Sprite):
    def __init__(self, groups, surf):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(center=(randint(0, WINDOW_WIDTH), randint(0, WINDOW_HEIGHT)))
        
class Laser(pygame.sprite.Sprite):

    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(midbottom=pos)
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, dt):
        self.rect.centery -= 400 * dt
        #This cleans any unseen lasers
        if self.rect.bottom < 0:
            self.kill()
    
class Meteor(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.original_surf = pygame.image.load(r"C:\Users\sebas\Desktop\personal\5games-main\space shooter\images\meteor.png").convert_alpha()
        self.image = surf
        self.rect = self.image.get_frect(center = pos)
        self.start_time = pygame.time.get_ticks()
        self.lifetime = 3000
        self.direction = pygame.Vector2(uniform(-0.5, 0.5),1)
        self.speed = randint(400,500)
        self.rotation = 0

        self.mask = pygame.mask.from_surface(self.image)
    
    def update(self, dt):
        self.rect.center += self.direction * self.speed * dt
        #Laser logic would be more efficient
        if pygame.time.get_ticks() - self.start_time >= self.lifetime:
            self.kill()
        self.rotation += randint(40, 100) * dt
        self.image = pygame.transform.rotozoom(self.original_surf, self.rotation, 1)
        #Override hitbox to match the rotating
        self.rect = self.image.get_frect(center = self.rect.center)

class Teto(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(center = pos)
        self.mask = pygame.mask.from_surface(self.image)

class AnimatedExplosion(pygame.sprite.Sprite):
    def __init__(self, frames, pos, groups):
        super().__init__(groups)
        self.frames = frames
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_frect(center = pos)

    def update(self, dt):
        self.frame_index += 25 * dt
        if self.frame_index < len(self.frames):
            self.image = self.frames[int(self.frame_index)]  #You can % by len to keep the animation looping indefinitley
        else:
            self.kill()

def collisions():
    global game_active, final_score, upgrades, meteor_score #Not a good way to do it, but since it's first game I will keep it as a global variable
    collision_sprites = pygame.sprite.spritecollide(player, meteor_sprites, True, pygame.sprite.collide_mask) #Masks are hardware intensive, so only used when necesarry
    if collision_sprites:
        final_score = int((pygame.time.get_ticks() - game_start_time) // 100) + meteor_score
        damage_sound.play() #Not necessary since player dies but just practicing importing sounds so idc
        game_active = False

    upgrade_touch = pygame.sprite.spritecollide(player, teto_sprites, True)
    if upgrade_touch:
        upgrades = 2

    for laser in laser_sprites:
        collided_sprites = pygame.sprite.spritecollide(laser, meteor_sprites, True) #Store collisions to break the laser too
        if collided_sprites:
            meteor_score += 10
            AnimatedExplosion(explosion_frames,laser.rect.midtop, all_sprites)
            explosion_sound.play()
            laser.kill()

def display_score():
    current_time = int(pygame.time.get_ticks() - game_start_time) // 100
    score = current_time + meteor_score
    text_surface = font.render(str(f"Score: {score}"), True, (255, 255, 255))
    text_rect = text_surface.get_frect(midbottom=(WINDOW_WIDTH/2, WINDOW_HEIGHT - 10))
    display_surface.blit(text_surface, text_rect)
    pygame.draw.rect(display_surface, (255, 255, 255), text_rect.inflate(20, 10), 2, border_radius=9) #Draws a rectangle around the text with a border of 2 pixels

def game_over():
    display_surface.fill("#221b25") 
    #Pop up rect
    popup_rect = pygame.Rect(0, 0, 450, 250) 
    popup_rect.center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2) 
    pygame.draw.rect(display_surface, "#3a2e3f", popup_rect, border_radius=15) 
    pygame.draw.rect(display_surface, (255, 255, 255), popup_rect, 3, border_radius=15) 

    #GG Text
    game_over_surf = game_over_font.render("GAME OVER", True, (255, 100, 100)) 
    game_over_rect = game_over_surf.get_frect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 - 50)) 
        
    #Final Score Text
    final_score_surf = font.render(f"Final Score: {final_score}", True, (255, 255, 255)) 
    final_score_rect = final_score_surf.get_frect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 + 10)) 

    #Restart Text
    restart_surf = font.render("Press R to restart the game", True, (255, 255, 255))
    restart_rect = restart_surf.get_frect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 + 60))

    #Show the pop up and final score
    display_surface.blit(game_over_surf, game_over_rect) 
    display_surface.blit(final_score_surf, final_score_rect) 
    display_surface.blit(restart_surf, restart_rect) 

def reset_game():
    global game_active, final_score, game_start_time, player, meteor_score, upgrades # Declare them global
    game_active = True
    meteor_score = 0
    final_score = 0
    upgrades = 1
    game_start_time = pygame.time.get_ticks() # Reset the timer baseline here!
    all_sprites.empty()
    meteor_sprites.empty()
    laser_sprites.empty()
    teto_sprites.empty()
    draw_stars()
    player = Player() # This now updates the global player variable
    all_sprites.add(player)

#General setup
pygame.init()
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Space Shooter")
running = True
clock = pygame.time.Clock() #Controls the frame rate of the game, you can use clock.tick(FPS) to limit the frame rate to a certain number of frames per second
game_active = True
final_score = 0
x = 100
y = 100
game_start_time = 0
upgrades = 1
meteor_score = 0

all_sprites = pygame.sprite.Group() #This creates a group of sprites, which is a collection of sprites that can be updated and drawn together, you can add sprites to the group using all_sprites.add(sprite) and remove them using all_sprites.remove(sprite), you can also use all_sprites.empty() to remove all sprites from the group
meteor_sprites = pygame.sprite.Group() #This creates a group of sprites, which is a collection of sprites that can be updated and drawn together, you can add sprites to the group using all_sprites.add(sprite) and remove them using all_sprites.remove(sprite), you can also use all_sprites.empty() to remove all sprites from the group
laser_sprites = pygame.sprite.Group()
teto_sprites = pygame.sprite.Group()
laser_surf = pygame.image.load(r"C:\Users\sebas\Desktop\personal\5games-main\space shooter\images\laser.png").convert_alpha()
meteor_surf = pygame.image.load(r"C:\Users\sebas\Desktop\personal\5games-main\space shooter\images\meteor.png").convert_alpha()
meteor_rect = meteor_surf.get_frect(center= (WINDOW_WIDTH/2 , WINDOW_HEIGHT /2) )
star_surf = pygame.image.load(r"C:\Users\sebas\Desktop\personal\5games-main\space shooter\images\star.png").convert_alpha()
teto_surf = pygame.image.load(r"C:\Users\sebas\Desktop\personal\5games-main\space shooter\images\Teto-Plush-Style-B-100x100-1078207073.png").convert_alpha()
teto_rect = teto_surf.get_frect(center = (WINDOW_WIDTH/2 , WINDOW_HEIGHT /2))
explosion_frames = [pygame.image.load(join(r"C:\Users\sebas\Desktop\personal\5games-main\space shooter\images\explosion", f"{i}.png")).convert_alpha() for i in range(21)] #Creates a list of every png in the explosion folder

#Sound files import
laser_sound = pygame.mixer.Sound(join(r"C:\Users\sebas\Desktop\personal\5games-main\space shooter\audio\laser.wav"))
laser_sound.set_volume(0.1)
explosion_sound = pygame.mixer.Sound(join(r"C:\Users\sebas\Desktop\personal\5games-main\space shooter\audio\explosion.wav"))
damage_sound = pygame.mixer.Sound(join(r"C:\Users\sebas\Desktop\personal\5games-main\space shooter\audio\damage.ogg"))
game_music = pygame.mixer.Sound(join(r"C:\Users\sebas\Desktop\personal\5games-main\space shooter\audio\game_music.wav"))
game_music.set_volume(0.01)
game_music.play()

font = pygame.font.Font(None, 20)
game_over_font = pygame.font.Font(None, 50)



def draw_stars():
    for i in range(20):
        Star(all_sprites, star_surf) #This creates 20 instances of the Star class and adds them to the all_sprites group, this will create 20 stars with random positions on the screen

draw_stars()
player = Player() #Creating an instance of the Player class, this will create a new player object with its own image and rect
all_sprites.add(player)

#Custom events -> Meteor event
meteor_event = pygame.event.custom_type() #This creates a new custom event type, you can use this to create your own events that can be triggered by the game, you can also use pygame.event.post(event) to post an event to the event queue, this will trigger the event and call any event handlers that are listening for that event
pygame.time.set_timer(meteor_event, 500) #This sets a timer for when to trigger the event
upgrade_event = pygame.event.custom_type()
pygame.time.set_timer(upgrade_event, 25000)

#Main loop
while running:
    dt = clock.tick() /1000
    #Event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == meteor_event:
            x, y = randint(0, WINDOW_WIDTH), randint(-200, -100) #Makes sure player has time to react
            Meteor(meteor_surf, (x, y), (all_sprites, meteor_sprites))
        if event.type == upgrade_event:
            x, y = randint(0, WINDOW_WIDTH), randint(100, 300)
            Teto(teto_surf, (x, y), (all_sprites, teto_sprites))

    if game_active:
        all_sprites.update(dt) #This updates all the sprites in the all_sprites group, you can also use all_sprites.draw(display_surface) to draw all the sprites in the group on the display surface
        collisions()
        #Draw the game
        display_surface.fill("#3a2e3f")
        display_score()
        all_sprites.draw(display_surface) #This draws all the sprites in the all_sprites group on the display surface, you can also use all_sprites.update() to update all the sprites in the group, this is useful for moving the sprites or changing their images

    else:
        game_over()
        if pygame.key.get_pressed()[pygame.K_r]: 
            reset_game() #This resets the game by clearing all the sprites and resetting the score, you can also use this to reset the game state to its initial state

    pygame.display.update() #This updates the display with everything that has been drawn since the last update, you can also use pygame.display.flip() which does the same thing but is a bit slower and only for a section

pygame.quit() #The opposite of pygame.init(), this uninitializes all pygame modules, you should always call this at the end of your program